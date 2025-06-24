from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction
import json
from datetime import datetime

def generate_sale_code():
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(sale_id) FROM SALE WHERE sale_id LIKE 'BL_%'")
        last_sale_result = cursor.fetchone()
        if last_sale_result and last_sale_result[0]:
            try:
                last_num = int(last_sale_result[0].split('_')[1])
            except Exception:
                last_num = 0
        else:
            last_num = 0
        return f"BL_{last_num + 1:02d}"

@login_required
def sales_view(request):
    return render(request, 'sales/sales.html')

@login_required
def get_sales_data(request):
    pharmacy_id = request.GET.get('pharmacy_id', '')
    period = request.GET.get('period', '')
    year = request.GET.get('year', '2024')
    user = request.user
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM SALE")
            sale_count = cursor.fetchone()[0]

            if sale_count == 0:
                return JsonResponse({
                    'success': True,
                    'data': [],
                    'total': 0,
                    'columns': ['id', 'name', 'location', 'sale_price', 'period'],
                    'message': 'No sales data found in database'
                })

            period_date = None
            if period:
                try:
                    month_num = datetime.strptime(period, '%B').month
                    period_date = f"{year}-{month_num:02d}-01"
                except:
                    period_date = None

            rows = []
            columns = []

            if pharmacy_id:
                pharmacy_id_int = int(pharmacy_id)
                cursor.execute("SELECT COUNT(*) FROM SALE WHERE pharmacyid = %s", [pharmacy_id_int])
                pharmacy_sales_count = cursor.fetchone()[0]

                if pharmacy_sales_count == 0:
                    return JsonResponse({
                        'success': True,
                        'data': [],
                        'total': 0,
                        'columns': ['id', 'name', 'location', 'sale_price', 'period'],
                        'message': f'No sales data found for pharmacy {pharmacy_id_int}'
                    })

                if period_date:
                    cursor.execute("CALL SALES(%s, %s)", [pharmacy_id_int, period_date])
                else:
                    cursor.execute("CALL SALES(%s, NULL)", [pharmacy_id_int])

                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            else:
                if user.is_superuser or getattr(user, 'role', '').upper() == 'ADMIN':
                    if period_date:
                        cursor.execute("CALL SALES(NULL, %s)", [period_date])
                    else:
                        cursor.execute("CALL SALES(NULL, NULL)")
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                else:
                    assigned_pharmacy_ids = set()

                    cursor.execute("SELECT assigned_pharmacy_id FROM accounts_customuser WHERE id = %s", [user.id])
                    result = cursor.fetchone()
                    if result and result[0]:
                        assigned_pharmacy_ids.add(result[0])

                    cursor.execute("SELECT pharmacy_id FROM pharmacies_pharmacy_managers WHERE customuser_id = %s", [user.id])
                    managed_pharmacies = cursor.fetchall()
                    assigned_pharmacy_ids.update([row[0] for row in managed_pharmacies])

                    if not assigned_pharmacy_ids:
                        return JsonResponse({'success': True, 'data': [], 'total': 0, 'columns': []})

                    all_rows = []
                    for p_id in assigned_pharmacy_ids:
                        cursor.execute("CALL SALES(%s, %s)", [p_id, period_date or None])
                        if not columns:
                            columns = [col[0] for col in cursor.description]
                        all_rows.extend(cursor.fetchall())
                    rows = all_rows

            data = []
            total_sales = 0
            for row in rows:
                row_dict = dict(zip(columns, row))
                data.append(row_dict)
                if 'sale_price' in row_dict and row_dict['sale_price']:
                    try:
                        total_sales += float(row_dict['sale_price'])
                    except:
                        pass

            if data:
                total_row = {col: '' for col in columns}
                total_row[columns[0]] = 'TOTAL'
                total_row['sale_price'] = total_sales
                data.append(total_row)

            return JsonResponse({
                'success': True,
                'data': data,
                'total': total_sales,
                'columns': columns
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
def submit_sale(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sales = data.get('sales')

            if not sales or not isinstance(sales, list):
                return JsonResponse({'success': False, 'error': 'No sales data provided'})

            sale_code = generate_sale_code()

            with transaction.atomic(), connection.cursor() as cursor:
                cursor.execute("SELECT assigned_pharmacy_id FROM accounts_customuser WHERE id = %s", [request.user.id])
                result = cursor.fetchone()

                if not result or not result[0]:
                    raise Exception('User has no assigned pharmacy')

                assigned_pharmacy_id = result[0]

                for sale_item in sales:
                    prd_name = sale_item.get('prd_name')
                    qty = int(sale_item.get('qty'))
                    total_price = int(sale_item.get('total_price'))
                    prd_code = sale_item.get('prd_code')
                    user_id = request.user.id

                    if not prd_code:
                        raise Exception(f"Product code is missing for item: {prd_name}")

                    cursor.execute(
                        "SELECT QTY FROM inventory WHERE PRD_code = %s AND ID = %s FOR UPDATE",
                        [prd_code, assigned_pharmacy_id]
                    )
                    stock_result = cursor.fetchone()

                    if stock_result is None:
                        raise Exception(f"Product '{prd_name}' not found in your pharmacy's inventory.")

                    current_qty = stock_result[0]
                    if current_qty < qty:
                        raise Exception(f"Not enough stock for {prd_name}. Available: {current_qty}, Requested: {qty}")

                    cursor.execute(
                        "UPDATE inventory SET QTY = QTY - %s WHERE PRD_code = %s AND ID = %s",
                        [qty, prd_code, assigned_pharmacy_id]
                    )

                    cursor.execute(
                        "INSERT INTO SALE (sale_id, prd_name, qty, price, pharmacyid, staff_id) VALUES (%s, %s, %s, %s, %s, %s)",
                        [sale_code, prd_name, qty, total_price, assigned_pharmacy_id, user_id]
                    )

            return JsonResponse({'success': True, 'sale_code': sale_code, 'message': 'All sales added successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
