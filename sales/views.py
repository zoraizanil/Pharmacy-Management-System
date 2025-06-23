from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import connection, transaction
import json
from datetime import datetime

def generate_sale_code():
    # Get the max sale_id that starts with BL_ using raw SQL
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
        return f"BL_{last_num+1:02d}"

@login_required
def sales_view(request):
    """Render the sales page with dropdown and calendar"""
    return render(request, 'sales/sales.html')

@login_required
def get_sales_data(request):
    """API endpoint to get sales data with filtering"""
    pharmacy_id = request.GET.get('pharmacy_id', '')
    period = request.GET.get('period', '')
    year = request.GET.get('year', '2024')  # Default to 2024 if not provided
    user = request.user
    
    print(f"🔍 get_sales_data called - pharmacy_id: '{pharmacy_id}', period: '{period}', year: '{year}', user: {user}")
    
    try:
        with connection.cursor() as cursor:
            rows = []
            columns = []
            # First, let's check if there's any sales data at all
            cursor.execute("SELECT COUNT(*) FROM SALE")
            sale_count = cursor.fetchone()[0]
            print(f"🔍 Total sales records in SALE table: {sale_count}")
            
            if sale_count == 0:
                print("🔍 No sales data found in SALE table")
                return JsonResponse({
                    'success': True, 
                    'data': [], 
                    'total': 0,
                    'columns': ['id', 'name', 'location', 'sale_price', 'period'],
                    'message': 'No sales data found in database'
                })
            
            # Convert period from month name to date format using the selected year
            period_date = None
            if period:
                try:
                    # Convert month name to a date in the selected year
                    from datetime import datetime
                    month_num = datetime.strptime(period, '%B').month
                    period_date = f"{year}-{month_num:02d}-01"
                    print(f"🔍 Converted period '{period}' to date: {period_date}")
                except Exception as e:
                    print(f"🔍 Error converting period: {e}")
                    period_date = None
            
            # Try different ways to call the procedure
            if pharmacy_id:
                # Execute procedure for specific pharmacy
                try:
                    pharmacy_id_int = int(pharmacy_id)
                    print(f"🔍 Selected pharmacy_id: {pharmacy_id} -> converted to int: {pharmacy_id_int}")
                    
                    # Test: Check what sales data exists for this pharmacy
                    cursor.execute("SELECT COUNT(*) FROM SALE WHERE pharmacyid = %s", [pharmacy_id_int])
                    pharmacy_sales_count = cursor.fetchone()[0]
                    print(f"🔍 Sales records for pharmacy {pharmacy_id_int}: {pharmacy_sales_count}")
                    
                    if pharmacy_sales_count == 0:
                        print(f"🔍 No sales data found for pharmacy {pharmacy_id_int}")
                        return JsonResponse({
                            'success': True, 
                            'data': [], 
                            'total': 0,
                            'columns': ['id', 'name', 'location', 'sale_price', 'period'],
                            'message': f'No sales data found for pharmacy {pharmacy_id_int}'
                        })
                    
                    if period_date:
                        sql = "EXEC sales @id=%s, @period=%s"
                        params = [pharmacy_id_int, period_date]
                    else:
                        sql = "EXEC sales @id=%s, @period=%s"
                        params = [pharmacy_id_int, None]
                    cursor.execute(sql, params)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    
                except ValueError:
                    print(f"🔍 Invalid pharmacy_id: {pharmacy_id}")
                    return JsonResponse({'success': True, 'data': [], 'total': 0})
                    
            else:
                # Execute procedure for all pharmacies (admin/superuser) or user's assigned pharmacies
                if user.is_superuser or getattr(user, 'role', None) == 'ADMIN':
                    if period_date:
                        sql = "EXEC sales @id=%s, @period=%s"
                        params = [None, period_date]  # Use None for 'All Pharmacies'
                    else:
                        sql = "EXEC sales"
                        params = []
                    cursor.execute(sql, params if params else [])
                    
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()

                else:
                    # For managers/staff, aggregate sales from their assigned pharmacies
                    assigned_pharmacy_ids = set()
                    
                    # Get user's assigned pharmacy
                    cursor.execute("SELECT assigned_pharmacy_id FROM accounts_customuser WHERE id = %s", [user.id])
                    assigned_pharmacy_result = cursor.fetchone()
                    if assigned_pharmacy_result and assigned_pharmacy_result[0]:
                        assigned_pharmacy_ids.add(assigned_pharmacy_result[0])
                    
                    # Get pharmacies managed by user
                    cursor.execute("""
                        SELECT pharmacy_id 
                        FROM pharmacies_pharmacy_managers 
                        WHERE customuser_id = %s
                    """, [user.id])
                    managed_pharmacies = cursor.fetchall()
                    assigned_pharmacy_ids.update([row[0] for row in managed_pharmacies])

                    if not assigned_pharmacy_ids:
                        return JsonResponse({'success': True, 'data': [], 'total': 0, 'columns': []})

                    all_rows = []
                    columns = []
                    for p_id in assigned_pharmacy_ids:
                        cursor.execute("EXEC sales @id=%s, @period=%s", [p_id, period_date or None])
                        if not columns:
                            columns = [col[0] for col in cursor.description]
                        all_rows.extend(cursor.fetchall())
                    rows = all_rows
            
            # Fetch results (this part is now inside the if/else for admin/manager)
            print(f"🔍 Query returned {len(rows)} rows with columns: {columns}")
            
            # Convert to list of dictionaries
            data = []
            total_sales = 0
            for row in rows:
                row_dict = dict(zip(columns, row))
                data.append(row_dict)
                # Sum sale_price column if it exists
                if 'sale_price' in row_dict and row_dict['sale_price']:
                    try:
                        total_sales += float(row_dict['sale_price'])
                    except (ValueError, TypeError):
                        pass
            
            # Add total row
            if data:
                total_row = {col: '' for col in columns}
                total_row[columns[0]] = 'TOTAL'
                total_row['sale_price'] = total_sales
                data.append(total_row)
            
            print(f"🔍 Returning {len(data)} rows with total sales: {total_sales}")
            
            return JsonResponse({
                'success': True, 
                'data': data, 
                'total': total_sales,
                'columns': columns
            })
            
    except Exception as e:
        print(f"🔍 Error in get_sales_data: {str(e)}")
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

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

            with transaction.atomic():
                # Get user's assigned pharmacy using raw SQL
                with connection.cursor() as cursor:
                    cursor.execute("SELECT assigned_pharmacy_id FROM accounts_customuser WHERE id = %s", [request.user.id])
                    assigned_pharmacy_result = cursor.fetchone()
                    
                    if not assigned_pharmacy_result or not assigned_pharmacy_result[0]:
                        raise Exception('User has no assigned pharmacy')
                    
                    assigned_pharmacy_id = assigned_pharmacy_result[0]

                    for sale_item in sales:
                        prd_name = sale_item.get('prd_name')
                        qty = int(sale_item.get('qty'))
                        total_price = int(sale_item.get('total_price'))
                        prd_code = sale_item.get('prd_code')
                        user_id = request.user.id

                        if not prd_code:
                            raise Exception(f"Product code is missing for item: {prd_name}")

                        # 1. Check stock and lock row with raw SQL using SQL Server syntax
                        cursor.execute(
                            "SELECT QTY FROM inventory WITH (UPDLOCK) WHERE PRD_code = %s AND ID = %s",
                            [prd_code, assigned_pharmacy_id]
                        )
                        result = cursor.fetchone()

                        if result is None:
                            raise Exception(f"Product '{prd_name}' not found in your pharmacy's inventory.")
                        
                        current_qty = result[0]
                        if current_qty < qty:
                            raise Exception(f"Not enough stock for {prd_name}. Available: {current_qty}, Requested: {qty}")

                        # 2. Update Inventory with raw SQL
                        cursor.execute(
                            "UPDATE inventory SET QTY = QTY - %s WHERE PRD_code = %s AND ID = %s",
                            [qty, prd_code, assigned_pharmacy_id]
                        )

                        # 3. Create the Sale record using raw SQL
                        cursor.execute("""
                            INSERT INTO SALE (sale_id, prd_name, qty, price, pharmacyid, staff_id)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, [sale_code, prd_name, qty, total_price, assigned_pharmacy_id, user_id])

            return JsonResponse({'success': True, 'sale_code': sale_code, 'message': 'All sales added successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
