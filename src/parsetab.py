
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'COMMA DATA DOT EQUALS ID LPAREN PROC RPAREN RUN SEMICOLON SET STRINGprogram : stmt_liststmt_list : stmt_list stmt\n    | stmtstmt : data_stepdata_step : DATA ID SEMICOLON data_body RUN SEMICOLONdata_body : stmt_list_datastmt_list_data : stmt_list_data stmt_data\n    | stmt_datastmt_data : set_stmt\n    | assignment_stmtset_stmt : SET qualified_id SEMICOLONset_stmt : SET ID SEMICOLONqualified_id : ID DOT IDassignment_stmt : ID EQUALS expr SEMICOLONexpr : function_callexpr : IDexpr : STRINGfunction_call : ID LPAREN expr_arg_list_opt RPARENexpr_arg_list_opt : expr_list\n    |expr_list : exprexpr_list : expr_list COMMA expr'
    
_lr_action_items = {'DATA':([0,2,3,4,6,25,],[5,5,-3,-4,-2,-5,]),'$end':([1,2,3,4,6,25,],[0,-1,-3,-4,-2,-5,]),'ID':([5,8,11,12,13,14,15,16,18,26,27,28,29,30,36,],[7,9,9,-8,-9,-10,20,21,-7,-11,-12,31,21,-14,21,]),'SEMICOLON':([7,17,19,20,21,22,23,24,31,35,],[8,25,26,27,-16,30,-15,-17,-13,-18,]),'SET':([8,11,12,13,14,18,26,27,30,],[15,15,-8,-9,-10,-7,-11,-12,-14,]),'EQUALS':([9,],[16,]),'RUN':([10,11,12,13,14,18,26,27,30,],[17,-6,-8,-9,-10,-7,-11,-12,-14,]),'STRING':([16,29,36,],[24,24,24,]),'DOT':([20,],[28,]),'COMMA':([21,23,24,33,34,35,37,],[-16,-15,-17,36,-21,-18,-22,]),'RPAREN':([21,23,24,29,32,33,34,35,37,],[-16,-15,-17,-20,35,-19,-21,-18,-22,]),'LPAREN':([21,],[29,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'program':([0,],[1,]),'stmt_list':([0,],[2,]),'stmt':([0,2,],[3,6,]),'data_step':([0,2,],[4,4,]),'data_body':([8,],[10,]),'stmt_list_data':([8,],[11,]),'stmt_data':([8,11,],[12,18,]),'set_stmt':([8,11,],[13,13,]),'assignment_stmt':([8,11,],[14,14,]),'qualified_id':([15,],[19,]),'expr':([16,29,36,],[22,34,37,]),'function_call':([16,29,36,],[23,23,23,]),'expr_arg_list_opt':([29,],[32,]),'expr_list':([29,],[33,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> stmt_list','program',1,'p_program','sasparser.py',147),
  ('stmt_list -> stmt_list stmt','stmt_list',2,'p_stmt_list','sasparser.py',152),
  ('stmt_list -> stmt','stmt_list',1,'p_stmt_list','sasparser.py',153),
  ('stmt -> data_step','stmt',1,'p_stmt','sasparser.py',162),
  ('data_step -> DATA ID SEMICOLON data_body RUN SEMICOLON','data_step',6,'p_data_step','sasparser.py',168),
  ('data_body -> stmt_list_data','data_body',1,'p_data_body','sasparser.py',174),
  ('stmt_list_data -> stmt_list_data stmt_data','stmt_list_data',2,'p_stmt_list_data','sasparser.py',179),
  ('stmt_list_data -> stmt_data','stmt_list_data',1,'p_stmt_list_data','sasparser.py',180),
  ('stmt_data -> set_stmt','stmt_data',1,'p_stmt_data','sasparser.py',189),
  ('stmt_data -> assignment_stmt','stmt_data',1,'p_stmt_data','sasparser.py',190),
  ('set_stmt -> SET qualified_id SEMICOLON','set_stmt',3,'p_set_stmt_qualified','sasparser.py',196),
  ('set_stmt -> SET ID SEMICOLON','set_stmt',3,'p_set_stmt_simple','sasparser.py',201),
  ('qualified_id -> ID DOT ID','qualified_id',3,'p_qualified_id','sasparser.py',207),
  ('assignment_stmt -> ID EQUALS expr SEMICOLON','assignment_stmt',4,'p_assignment_stmt','sasparser.py',213),
  ('expr -> function_call','expr',1,'p_expr_function_call','sasparser.py',219),
  ('expr -> ID','expr',1,'p_expr_identifier','sasparser.py',224),
  ('expr -> STRING','expr',1,'p_expr_string','sasparser.py',229),
  ('function_call -> ID LPAREN expr_arg_list_opt RPAREN','function_call',4,'p_function_call','sasparser.py',235),
  ('expr_arg_list_opt -> expr_list','expr_arg_list_opt',1,'p_expr_arg_list_opt','sasparser.py',241),
  ('expr_arg_list_opt -> <empty>','expr_arg_list_opt',0,'p_expr_arg_list_opt','sasparser.py',242),
  ('expr_list -> expr','expr_list',1,'p_expr_list_single','sasparser.py',250),
  ('expr_list -> expr_list COMMA expr','expr_list',3,'p_expr_list_multiple','sasparser.py',255),
]
