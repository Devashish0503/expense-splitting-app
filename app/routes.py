from flask import Blueprint, jsonify, request
from app.models import Expense
from app.services import ExpenseService, SettlementService

main_bp = Blueprint('main', __name__)

# API response helper
def api_response(success, data=None, message=""):
    response = {
        "success": success,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response)

# Expense Management Routes
@main_bp.route('/expenses', methods=['GET'])
def get_expenses():
    try:
        expenses = ExpenseService.get_all_expenses()
        return api_response(
            success=True,
            data=[expense.to_dict() for expense in expenses],
            message="Expenses retrieved successfully"
        )
    except Exception as e:
        return api_response(success=False, message=f"Failed to retrieve expenses: {str(e)}"), 500

@main_bp.route('/expenses', methods=['POST'])
def create_expense():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('amount'):
            return api_response(success=False, message="Amount is required"), 400
            
        if float(data.get('amount', 0)) <= 0:
            return api_response(success=False, message="Amount must be greater than 0"), 400
            
        if not data.get('description'):
            return api_response(success=False, message="Description is required"), 400
            
        if not data.get('paid_by'):
            return api_response(success=False, message="Paid by is required"), 400
        
        # Create expense
        expense = ExpenseService.create_expense(data)
        
        return api_response(
            success=True,
            data=expense.to_dict(),
            message="Expense added successfully"
        ), 201
    except Exception as e:
        return api_response(success=False, message=f"Failed to create expense: {str(e)}"), 500

@main_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    try:
        data = request.json
        
        # Validate amount if provided
        if 'amount' in data and float(data.get('amount', 0)) <= 0:
            return api_response(success=False, message="Amount must be greater than 0"), 400
            
        # Update expense
        expense = ExpenseService.update_expense(expense_id, data)
        
        if not expense:
            return api_response(success=False, message="Expense not found"), 404
            
        return api_response(
            success=True,
            data=expense.to_dict(),
            message="Expense updated successfully"
        )
    except Exception as e:
        return api_response(success=False, message=f"Failed to update expense: {str(e)}"), 500

@main_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        result = ExpenseService.delete_expense(expense_id)
        
        if not result:
            return api_response(success=False, message="Expense not found"), 404
            
        return api_response(
            success=True,
            message="Expense deleted successfully"
        )
    except Exception as e:
        return api_response(success=False, message=f"Failed to delete expense: {str(e)}"), 500

# Settlement Routes
@main_bp.route('/people', methods=['GET'])
def get_people():
    try:
        people = SettlementService.get_all_people()
        return api_response(
            success=True,
            data=people,
            message="People retrieved successfully"
        )
    except Exception as e:
        return api_response(success=False, message=f"Failed to retrieve people: {str(e)}"), 500

@main_bp.route('/balances', methods=['GET'])
def get_balances():
    try:
        balances = SettlementService.calculate_balances()
        return api_response(
            success=True,
            data=balances,
            message="Balances calculated successfully"
        )
    except Exception as e:
        return api_response(success=False, message=f"Failed to calculate balances: {str(e)}"), 500

@main_bp.route('/settlements', methods=['GET'])
def get_settlements():
    try:
        settlements = SettlementService.calculate_settlements()
        return api_response(
            success=True,
            data=settlements,
            message="Settlements calculated successfully"
        )
    except Exception as e:
        return api_response(success=False, message=f"Failed to calculate settlements: {str(e)}"), 500
