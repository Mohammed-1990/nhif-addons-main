# -*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime


class ConsolidatedGroupStatement(models.AbstractModel):
    _name = 'report.kamil_accounting_reports.consolidated_g_stm_temp'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        account_id = data['form']['account_id']
        company_ids = data['form']['company_ids']
        selected_company_ids = data['form']['selected_company_ids']
        len_company_ids = len(company_ids)
        company_id_logo = self.env.user.company_id.logo

        selected_company_names = []
        for company_id in self.env['res.company'].search([('id', 'in', selected_company_ids)]):
            selected_company_names.append(company_id.short_name or company_id.name)

        account_id = self.env['account.account'].search([('id', '=', account_id)])[0]
        account_type = ''
        if account_id.code[:1] == '1':
            account_type = 'revenues'
        elif account_id.code[:1] == '2':
            account_type = 'expenses'
        elif account_id.code[:1] == '3':
            account_type = 'assets'
        elif account_id.code[:1] == '4':
            account_type = 'liabilities'

        total_opening_balance = total_budget_value = total_total_debit = total_total_credit = total_period_net = total_total_balance = 0

        state_account_count_dict = {}
        branch_total_dict = {}

        group_account_lines = []
        group_account_ids_ = []
        group_account_lines_all = []

        for sub_account in self.env['account.account'].sudo().search(
                [('code', '=ilike', account_id.code + '%'),('company_id', '=', 9),
                 ('is_group', '=', 'group')]):
            if sub_account not in group_account_ids_ and sub_account != account_id:
                group_account_ids_.append(sub_account)



        for company_id in self.env['res.company'].sudo().search([('id', 'in', company_ids)]):

            state_account_count = 0
            branch_total = 0

            group_account_ids = []

            is_state_total_added = False

            all_accounts_list = []

            for sub_account in self.env['account.account'].sudo().search(
                    [('code', '=ilike', account_id.code + '%'),('company_id', '=', company_id.id),
                     ('is_group', '=', 'sub_account')]):
                for account in self.env['account.account'].sudo().search(
                        [('code', '=', sub_account.parent_budget_item_id.code),('company_id', '=', company_id.id)]):
                    if account not in group_account_ids and account != account_id:
                        group_account_ids.append(account)

            period_net = 0
            total_balance = 0
            for group_account in group_account_ids:

                group_opening_balance = group_budget_value = group_total_debit = group_total_credit = group_period_net = group_total_balance = 0

                # if group_account.id in all_accounts_list:
                # 	continue
                # else:
                # 	all_accounts_list.append(group_account.id)

                account_lines = []
                period_net = 0
                total_balance = 0
                for account in self.env['account.account'].sudo().search(
                        [('parent_budget_item_id.code', '=', group_account.code), ('is_group', '=', 'sub_account'),
                         ('company_id', '=', company_id.id)]):

                    # if account.id in all_accounts_list:
                    # 	continue
                    # else:
                    # 	all_accounts_list.append(account.id)

                    partners_balance_lines = []

                    opening_balance = budget_value = 0

                    if account_type in ['revenues', 'expenses']:
                        for budget in self.env['crossovered.budget'].sudo().search(
                                [('date_from', '<=', date_from), ('date_to', '>=', date_to),
                                 ('company_id', '=', company_id.id)]):
                            if account_type == 'expenses':
                                the_budget_type_line = budget.expenses_line_ids
                            if account_type == 'revenues':
                                the_budget_type_line = budget.revenues_line_ids
                            for budget_type_line in the_budget_type_line:
                                for budget_line in budget_type_line.general_budget_id.accounts_value_ids:
                                    if budget_line.account_id.id == account.id:
                                        found = True
                                        if budget_line.approved_value > 0:
                                            budget_value = budget_line.approved_value
                                            total_budget_value += budget_value
                                            group_budget_value += budget_value
                    balance_statement = ''
                    if account_type in ['assets', 'liabilities']:
                        if account_type == 'assets':
                            balance_statement = " sum(COALESCE( debit, 0 )) - sum(COALESCE( credit, 0 )) "
                        if account_type == 'liabilities':
                            balance_statement = " sum(COALESCE( credit, 0 )) - sum(COALESCE( debit, 0 )) "

                        self._cr.execute(
                            "SELECT  " + balance_statement + "  from account_move_line where account_id=" + str(
                                account.id) + " AND date <  '" + str(date_from) + "'  AND company_id = " + str(
                                company_id.id))

                        opening_balance = self.env.cr.fetchone()[0] or 0.0
                        total_opening_balance += opening_balance
                        group_opening_balance += opening_balance

                    self._cr.execute(
                        "SELECT COALESCE(sum(COALESCE( debit, 0 )), 0 ), COALESCE(sum(COALESCE( credit, 0 )), 0) from account_move_line where account_id=" + str(
                            account.id) + " AND date >= '" + str(date_from) + "' AND date <= '" + str(
                            date_to) + "' AND company_id = " + str(company_id.id))

                    all_balances = self.env.cr.fetchall()

                    total_debit = all_balances[0][0]
                    total_credit = all_balances[0][1]
                    total_total_debit += total_debit
                    total_total_credit += total_credit

                    group_total_debit += total_debit
                    group_total_credit += total_credit

                    period_net = 0
                    total_balance = 0

                    if account_type == 'assets':
                        period_net = total_debit - total_credit
                        total_balance = period_net + opening_balance
                        group_period_net += period_net
                        group_total_balance += total_balance

                    if account_type == 'liabilities':
                        period_net = total_credit - total_debit
                        total_balance = period_net + opening_balance
                        group_period_net += period_net
                        group_total_balance += total_balance

                    if account_type == 'revenues':
                        period_net = total_credit - total_debit
                        total_balance = total_credit - total_debit
                        group_period_net += period_net
                        group_total_balance += total_balance

                    if account_type == 'expenses':
                        period_net = total_debit - total_credit
                        total_balance = total_debit - total_credit
                        group_period_net += period_net
                        group_total_balance += total_balance

                    total_period_net += period_net
                    total_total_balance += total_balance

                    branch_total = branch_total + total_balance

                    if budget_value < 0:
                        budget_value = '(' + str('{:,.2f}'.format(abs(budget_value))) + ')'
                    else:
                        budget_value = str('{:,.2f}'.format(budget_value))

                    if opening_balance < 0:
                        opening_balance = '(' + str('{:,.2f}'.format(abs(opening_balance))) + ')'
                    else:
                        opening_balance = str('{:,.2f}'.format(opening_balance))

                    if total_debit < 0:
                        total_debit = '(' + str('{:,.2f}'.format(abs(total_debit))) + ')'
                    else:
                        total_debit = str('{:,.2f}'.format(total_debit))

                    if total_credit < 0:
                        total_credit = '(' + str('{:,.2f}'.format(abs(total_credit))) + ')'
                    else:
                        total_credit = str('{:,.2f}'.format(total_credit))

                    if period_net < 0:
                        period_net = '(' + str('{:,.2f}'.format(abs(period_net))) + ')'
                    else:
                        period_net = str('{:,.2f}'.format(period_net))

                    if total_balance < 0:
                        total_balance = '(' + str('{:,.2f}'.format(abs(total_balance))) + ')'
                    else:
                        total_balance = str('{:,.2f}'.format(total_balance))

                    if account.group_by_partners_in_reports:

                        self._cr.execute(
                            "SELECT DISTINCT COALESCE(partner_id,0) FROM account_move_line WHERE partner_id is not null and company_id = " + str(
                                company_id.id) + " and account_id  = " + str(account.id) + " ")

                        all_partners = self.env.cr.fetchall()
                        all_partners_list = []

                        pair_partners = []
                        for the_partner in all_partners:
                            partner = False
                            if len(the_partner) > 0:
                                for p in self.env['res.partner'].sudo().search([('id', '=', the_partner[0])]):
                                    partner = p

                            # partner = self.env['res.partner'].sudo().search([('id','=',the_partner[0])])[0]
                            if partner:
                                if partner.id not in all_partners_list:
                                    partner_ids = []
                                    all_partners_list.append(partner.id)

                                    partner_ids.append(partner.id)
                                    if partner.parent_id:
                                        partner_ids.append(partner.parent_id.id)
                                        all_partners_list.append(partner.parent_id.id)
                                    for child in partner.child_ids:
                                        partner_ids.append(child.id)
                                        all_partners_list.append(child.id)

                                    pair_partners.append(partner_ids)

                        for partner_ids_list in pair_partners:
                            partner_opening_balance = partner_total_debit = partner_total_credit = partner_period_net = partner_total_balance = 0

                            partner_name = ''

                            if len(partner_ids_list) == 1:
                                where_clause = " partner_id = " + str(partner_ids_list[0])

                                for name in self.env['res.partner'].search([('id', '=', partner_ids_list[0])]):
                                    partner_name = name.name

                            else:
                                where_clause = " partner_id in " + str(tuple(partner_ids_list))
                                for name in self.env['res.partner'].search([('id', 'in', partner_ids_list)]):
                                    partner_name = partner_name + ',' + name.name
                            if account_type in ['assets', 'liabilities']:
                                self._cr.execute(
                                    "SELECT  " + balance_statement + "  from account_move_line where account_id=" + str(
                                        account.id) + " AND date <  '" + str(date_from) + "'  AND company_id = " + str(
                                        company_id.id) + " AND " + where_clause)

                                partner_opening_balance = self.env.cr.fetchone()[0] or 0.0

                            self._cr.execute(
                                "SELECT COALESCE(sum(COALESCE( debit, 0 )), 0 ), COALESCE(sum(COALESCE( credit, 0 )), 0) from account_move_line where account_id=" + str(
                                    account.id) + " AND date >= '" + str(date_from) + "' AND date <= '" + str(
                                    date_to) + "' AND company_id = " + str(company_id.id) + " AND " + where_clause)

                            partner_all_balances = self.env.cr.fetchall()

                            partner_total_debit = partner_all_balances[0][0]
                            partner_total_credit = partner_all_balances[0][1]

                            if account_type == 'assets':
                                partner_period_net = partner_total_debit - partner_total_credit
                                partner_total_balance = partner_period_net + partner_opening_balance

                            if account_type == 'liabilities':
                                partner_period_net = partner_total_credit - partner_total_debit
                                partner_total_balance = partner_period_net + partner_opening_balance

                            if account_type == 'revenues':
                                partner_period_net = partner_total_credit - partner_total_debit
                                partner_total_balance = partner_total_credit - partner_total_debit

                            if account_type == 'expenses':
                                partner_period_net = partner_total_debit - partner_total_credit
                                partner_total_balance = partner_total_debit - partner_total_credit

                            if partner_opening_balance < 0:
                                partner_opening_balance = '(' + str(
                                    '{:,.2f}'.format(abs(partner_opening_balance))) + ')'
                            else:
                                partner_opening_balance = str('{:,.2f}'.format(partner_opening_balance))

                            if partner_total_debit < 0:
                                partner_total_debit = '(' + str('{:,.2f}'.format(abs(partner_total_debit))) + ')'
                            else:
                                partner_total_debit = str('{:,.2f}'.format(partner_total_debit))

                            if partner_total_credit < 0:
                                partner_total_credit_ = '(' + str('{:,.2f}'.format(abs(partner_total_credit))) + ')'
                            else:
                                partner_total_credit_ = str('{:,.2f}'.format(partner_total_credit))

                            if partner_period_net < 0:
                                partner_period_net = '(' + str('{:,.2f}'.format(abs(partner_period_net))) + ')'
                            else:
                                partner_period_net = str('{:,.2f}'.format(partner_period_net))

                            if partner_total_balance < 0:
                                partner_total_balance = '(' + str('{:,.2f}'.format(abs(partner_total_balance))) + ')'
                            else:
                                partner_total_balance = str('{:,.2f}'.format(partner_total_balance))
                            if partner_total_credit != 0:
                                partners_balance_lines.append({
                                    'partner_name': partner_name,
                                    'partner_opening_balance': partner_opening_balance,
                                    'partner_total_debit': partner_total_debit,
                                    'partner_total_credit': partner_total_credit_,
                                    'partner_period_net': partner_period_net,
                                    'partner_total_balance': partner_total_balance,
                                })
                    if total_credit != '0.00' or budget_value != '0.00':
                        account_lines.append({
                            'branch': company_id.short_name or company_id.name,
                            'branch_id': company_id.id,
                            'account_name': account.code + ' ' + account.name,
                            'clarification_number': account.clarification_number,
                            'account_id': account.id,
                            'budget_value': budget_value,
                            'opening_balance': opening_balance,
                            'total_debit': total_debit,
                            'total_credit': total_credit,
                            'period_net': period_net,
                            'total_balance': total_balance,
                            'group_by_partners_in_reports': account.group_by_partners_in_reports,
                            'partners_balance_lines': partners_balance_lines,
                        })

                state_account_count = state_account_count + 1
                if group_total_credit != 0 or group_budget_value != 0:
                    if group_budget_value < 0:
                        group_budget_value_state = '(' + str('{:,.2f}'.format(abs(group_budget_value))) + ')'
                    else:
                        group_budget_value_state = str('{:,.2f}'.format(group_budget_value))

                    if group_opening_balance < 0:
                        group_opening_balance_state = '(' + str('{:,.2f}'.format(abs(group_opening_balance))) + ')'
                    else:
                        group_opening_balance_state = str('{:,.2f}'.format(group_opening_balance))

                    if group_total_debit < 0:
                        group_total_debit_state = '(' + str('{:,.2f}'.format(abs(group_total_debit))) + ')'
                    else:
                        group_total_debit_state = str('{:,.2f}'.format(group_total_debit))

                    if group_total_credit < 0:
                        group_total_credit_state = '(' + str('{:,.2f}'.format(abs(group_total_credit))) + ')'
                    else:
                        group_total_credit_state = str('{:,.2f}'.format(group_total_credit))

                    if group_period_net < 0:
                        group_period_net_state = '(' + str('{:,.2f}'.format(abs(group_period_net))) + ')'
                    else:
                        group_period_net_state = str('{:,.2f}'.format(group_period_net))

                    if group_total_balance < 0:
                        group_total_balance_state = '(' + str('{:,.2f}'.format(abs(group_total_balance))) + ')'
                    else:
                        group_total_balance_state = str('{:,.2f}'.format(group_total_balance))

                    group_account_lines.append({
                        'branch': company_id.short_name or company_id.name,
                        'branch_id': company_id.id,
                        'branch_id_code': int(11223344556677) + group_account.id - company_id.id,
                        'account_id': group_account.id,
                        'parent_id': group_account.parent_budget_item_id.id,
                        'account_code': group_account.code,
                        'account_name': group_account.code + ' ' + group_account.name,
                        'clarification_number': group_account.clarification_number,
                        'budget_value': group_budget_value_state,
                        'budget_value_int': group_budget_value,
                        'opening_balance': group_opening_balance_state,
                        'opening_balance_int': group_opening_balance,
                        'total_debit': group_total_debit_state,
                        'total_credit': group_total_credit_state,
                        'total_debit_int': group_total_debit,
                        'total_credit_int': group_total_credit,
                        'period_net': group_period_net_state,
                        'period_net_int': group_period_net,
                        'total_balance': group_total_balance_state,
                        'total_balance_int': group_total_balance,
                        'account_lines': account_lines,
                        'is_state_total_added': is_state_total_added,
                    })

                if not is_state_total_added:
                    is_state_total_added = True

            state_account_count_dict[company_id.id] = state_account_count

            if branch_total < 0:
                branch_total = '(' + str('{:,.2f}'.format(abs(branch_total))) + ')'
            else:
                branch_total = str('{:,.2f}'.format(branch_total))

            branch_total_dict[company_id.id] = branch_total

        for group_account in group_account_ids_:
            group_opening_balance_ = group_budget_value_ = group_total_debit_ = group_total_credit_ = group_period_net_ = group_total_balance_ = 0
            for line in group_account_lines:
                if line['account_code'] == group_account.code:
                    group_budget_value_ += line['budget_value_int']
                    group_total_debit_ += line['total_debit_int']
                    group_total_credit_ += line['total_credit_int']
                    group_opening_balance_ += line['opening_balance_int']
                    group_period_net_ += line['period_net_int']
                    group_total_balance_ += line['total_balance_int']
            if group_total_credit_ != 0 or group_budget_value_ != 0:
                if group_budget_value_ < 0:
                    group_budget_value_state_ = '(' + str('{:,.2f}'.format(abs(group_budget_value_))) + ')'
                else:
                    group_budget_value_state_ = str('{:,.2f}'.format(group_budget_value_))

                if group_opening_balance_ < 0:
                    group_opening_balance_state_ = '(' + str('{:,.2f}'.format(abs(group_opening_balance_))) + ')'
                else:
                    group_opening_balance_state_ = str('{:,.2f}'.format(group_opening_balance_))

                if group_total_debit_ < 0:
                    group_total_debit_state_ = '(' + str('{:,.2f}'.format(abs(group_total_debit_))) + ')'
                else:
                    group_total_debit_state_ = str('{:,.2f}'.format(group_total_debit_))

                if group_total_credit_ < 0:
                    group_total_credit_state_ = '(' + str('{:,.2f}'.format(abs(group_total_credit_))) + ')'
                else:
                    group_total_credit_state_ = str('{:,.2f}'.format(group_total_credit_))

                if group_period_net_ < 0:
                    group_period_net_state_ = '(' + str('{:,.2f}'.format(abs(group_period_net_))) + ')'
                else:
                    group_period_net_state_ = str('{:,.2f}'.format(group_period_net_))

                if group_total_balance_ < 0:
                    group_total_balance_state_ = '(' + str('{:,.2f}'.format(abs(group_total_balance_))) + ')'
                else:
                    group_total_balance_state_ = str('{:,.2f}'.format(group_total_balance_))
                group_account_lines_all.append({
                    'account_name': group_account.code + ' ' + group_account.name,
                    'account_id': group_account.id,
                    'is_group': group_account.is_group,
                    'account_code': group_account.code,
                    'clarification_number': group_account.clarification_number,
                    'budget_value': group_budget_value_state_,
                    'opening_balance': group_opening_balance_state_,
                    'total_debit': group_total_debit_state_,
                    'total_credit': group_total_credit_state_,
                    'period_net': group_period_net_state_,
                    'total_balance': group_total_balance_state_,
                })

        if total_budget_value < 0:
            total_budget_value = '(' + str('{:,.2f}'.format(abs(total_budget_value))) + ')'
        else:
            total_budget_value = str('{:,.2f}'.format(total_budget_value))

        if total_opening_balance < 0:
            total_opening_balance = '(' + str('{:,.2f}'.format(abs(total_opening_balance))) + ')'
        else:
            total_opening_balance = str('{:,.2f}'.format(total_opening_balance))

        if total_total_debit < 0:
            total_total_debit = '(' + str('{:,.2f}'.format(abs(total_total_debit))) + ')'
        else:
            total_total_debit = str('{:,.2f}'.format(total_total_debit))

        if total_total_credit < 0:
            total_total_credit = '(' + str('{:,.2f}'.format(abs(total_total_credit))) + ')'
        else:
            total_total_credit = str('{:,.2f}'.format(total_total_credit))

        if total_period_net < 0:
            total_period_net = '(' + str('{:,.2f}'.format(abs(total_period_net))) + ')'
        else:
            total_period_net = str('{:,.2f}'.format(total_period_net))

        if total_total_balance < 0:
            total_total_balance = '(' + str('{:,.2f}'.format(abs(total_total_balance))) + ')'
        else:
            total_total_balance = str('{:,.2f}'.format(total_total_balance))

        return {
            'doc_model': data['model'],
            'date_from': date_from,
            'date_to': date_to,
            'account_type': account_type,
            'account_name': account_id.code + ' ' + account_id.name,

            'group_account_lines': group_account_lines,
            'group_account_lines_all': group_account_lines_all,

            'total_budget_value': total_budget_value,
            'total_opening_balance': total_opening_balance,
            'total_total_debit': total_total_debit,
            'total_total_credit': total_total_credit,
            'total_period_net': total_period_net,
            'total_total_balance': total_total_balance,
            'state_account_count_dict': state_account_count_dict,
            'branch_total_dict': branch_total_dict,
            'companies_len': len_company_ids,
            'company_id_logo': company_id_logo,
            'selected_company_names': selected_company_names,
        }


class Account(models.Model):
    _inherit = 'account.account'

    group_by_partners_in_reports = fields.Boolean()
