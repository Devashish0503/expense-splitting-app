from app import db
from app.models import Expense, Participant, SplitType

class ExpenseService:
    @staticmethod
    def create_expense(data):
        """Create a new expense with participants"""
        amount = data.get('amount')
        description = data.get('description')
        paid_by = data.get('paid_by')
        split_type = data.get('split_type', SplitType.EQUAL)
        category = data.get('category')
        
        # Create new expense
        expense = Expense(
            amount=amount,
            description=description,
            paid_by=paid_by,
            split_type=split_type,
            category=category
        )
        
        # Handle participant creation based on split type
        if 'participants' in data and data['participants']:
            # User provided specific participants with shares
            participants = data['participants']
            for p in participants:
                participant = Participant(
                    name=p['name'],
                    share=p['share']
                )
                expense.participants.append(participant)
        else:
            # Default: create equal split among participants
            # If participant_names not provided, use paid_by as only participant
            participant_names = data.get('participant_names', [paid_by])
            if paid_by not in participant_names:
                participant_names.append(paid_by)
                
            # Create equal split
            per_person_share = amount / len(participant_names)
            for name in participant_names:
                participant = Participant(
                    name=name,
                    share=round(per_person_share, 2)  # Round to 2 decimal places
                )
                expense.participants.append(participant)
        
        db.session.add(expense)
        db.session.commit()
        return expense

    @staticmethod
    def get_all_expenses():
        """Get all expenses"""
        return Expense.query.order_by(Expense.date.desc()).all()
        
    @staticmethod
    def get_expense_by_id(expense_id):
        """Get expense by ID"""
        return Expense.query.get(expense_id)
        
    @staticmethod
    def update_expense(expense_id, data):
        """Update an existing expense"""
        expense = Expense.query.get(expense_id)
        if not expense:
            return None
            
        # Update basic expense details
        if 'amount' in data:
            expense.amount = data['amount']
        if 'description' in data:
            expense.description = data['description']
        if 'paid_by' in data:
            expense.paid_by = data['paid_by']
        if 'category' in data:
            expense.category = data['category']
        if 'split_type' in data:
            expense.split_type = data['split_type']
            
        # If participants are updated, delete old ones and add new ones
        if 'participants' in data:
            # Delete old participants
            Participant.query.filter_by(expense_id=expense_id).delete()
            
            # Add new participants
            participants = data['participants']
            for p in participants:
                participant = Participant(
                    name=p['name'],
                    share=p['share'],
                    expense_id=expense_id
                )
                db.session.add(participant)
                
        db.session.commit()
        return expense
        
    @staticmethod
    def delete_expense(expense_id):
        """Delete an expense"""
        expense = Expense.query.get(expense_id)
        if expense:
            db.session.delete(expense)
            db.session.commit()
            return True
        return False

class SettlementService:
    @staticmethod
    def get_all_people():
        """Get all unique people from expenses"""
        # Get all expenses
        expenses = Expense.query.all()
        
        # Collect unique people names
        people_set = set()
        for expense in expenses:
            people_set.add(expense.paid_by)
            for participant in expense.participants:
                people_set.add(participant.name)
                
        return sorted(list(people_set))
        
    @staticmethod
    def calculate_balances():
        """Calculate balance for each person"""
        # Get all expenses
        expenses = Expense.query.all()
        
        # Calculate balances
        balance_map = {}
        
        for expense in expenses:
            payer = expense.paid_by
            amount = expense.amount
            
            # Add amount to payer
            if payer not in balance_map:
                balance_map[payer] = 0
            balance_map[payer] += amount
            
            # Subtract shares from participants
            for participant in expense.participants:
                name = participant.name
                share = participant.share
                
                if name not in balance_map:
                    balance_map[name] = 0
                balance_map[name] -= share
                
        # Convert to list of balances
        balances = [{"name": name, "net": round(balance, 2)} for name, balance in balance_map.items()]
        return balances
        
    @staticmethod
    def calculate_settlements():
        """Calculate simplest settlement plan"""
        # Get balances
        balances = SettlementService.calculate_balances()
        
        # Separate debtors (negative balance) and creditors (positive balance)
        debtors = [b for b in balances if b["net"] < 0]
        debtors.sort(key=lambda x: x["net"])  # Sort by ascending balance (most negative first)
        
        creditors = [b for b in balances if b["net"] > 0]
        creditors.sort(key=lambda x: x["net"], reverse=True)  # Sort by descending balance
        
        settlements = []
        debtor_index = 0
        creditor_index = 0
        
        # Create settlements by matching debtors with creditors
        while debtor_index < len(debtors) and creditor_index < len(creditors):
            debtor = debtors[debtor_index]
            creditor = creditors[creditor_index]
            
            # Calculate settlement amount (minimum of debt and credit)
            amount = min(abs(debtor["net"]), creditor["net"])
            amount = round(amount, 2)
            
            if amount > 0:
                # Create settlement
                settlements.append({
                    "from": debtor["name"],
                    "to": creditor["name"],
                    "amount": amount
                })
                
                # Update balances
                debtor["net"] += amount
                creditor["net"] -= amount
                
            # Move to next person if their balance is settled
            if abs(debtor["net"]) < 0.01:
                debtor_index += 1
                
            if abs(creditor["net"]) < 0.01:
                creditor_index += 1
                
        return settlements
