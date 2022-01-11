import ast

# Attribute(value=Name(id='self', ctx=Load()), attr='_generate_image', ctx=Load())

# Call(
#   func=Name(
#       id='tuple', ctx=Load()
#   ), args=[
#       Attribute(
#           value=Attribute(
#               value=Attribute(
#                   value=Name(id='game', ctx=Load()), attr='Game', ctx=Load()
#               ), attr='inst', ctx=Load()
#           ), attr='game_resolution', ctx=Load()
#       )
#   ], keywords=[])


script = open("arrow.py").read()

class NodeVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call):
        n = node.func
        parts = []
        while isinstance(n, ast.Attribute):
            parts.append(n.attr)
            #print(ast.dump(n))
            #print("diving deeper", ast.dump(n))
            n = n.value
            
        if isinstance(n, ast.Name):
            parts.append(n.id)

        #print(parts)
        if 'tuple' in parts:
            print(ast.dump(node))
            print(parts)
        self.generic_visit(node)
        #print(node.args)
        #if isinstance(node.func, ast.Name):
        #    print(node.func.id)
        #    print(node.args)


script_ast = ast.parse(script)
#print(ast.dump(script_ast))
NodeVisitor().visit(script_ast)
