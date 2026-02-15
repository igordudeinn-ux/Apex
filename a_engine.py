import re, os, time, random
from debugger import ApixDebugger as deb

class Apix_Compiler:
    def __init__(self):
        self.variables = {'true': True, 'false': False, 'null[]': None}
        self.functions = {}
        self.recording_for = None
        self.skip_stack = []
        self.return_value = None

    def eval_expr(self, expr, line_num, raw_line):
        expr = str(expr).strip()
        
        array_get = re.match(r'(\w+)\[(.*?)\]', expr)
        if array_get:
            name, idx_expr = array_get.groups()
            idx = self.eval_expr(idx_expr, line_num, raw_line)
            if name in self.variables and isinstance(self.variables[name], list):
                try:
                    return self.variables[name][int(idx)]
                except (IndexError, ValueError):
                    deb.report_error("Index Error", f"Invalid index '{idx}' for '{name}'", line_num, raw_line)
                    return None

        if expr == 'null[]': return None
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        
        try:
            temp_expr = re.sub(r'(?<![=!<>])=(?!=)', '==', expr)
            return eval(temp_expr, {"__builtins__": None}, self.variables)
        except NameError:
            deb.report_error("Name Error", f"Variable in '{expr}' is not defined", line_num, raw_line)
        except Exception as e:
            deb.report_error("Logic Error", f"{type(e).__name__}: {str(e)}", line_num, raw_line)
        return None

    def execute_line(self, line, line_num):
        raw_line = line.split('--')[0].strip()
        if not raw_line: return

        if raw_line == "}":
            if self.recording_for:
                name, start, end, body = self.recording_for
                self.recording_for = None
                for val in range(start, end + 1):
                    self.variables[name] = val
                    deb.log_var_change(name, val)
                    for b_line in body: self.execute_line(b_line, f"loop-{line_num}")
            elif self.skip_stack:
                self.skip_stack.pop()
            return

        if self.recording_for:
            self.recording_for[3].append(raw_line)
            return

        is_skipping = any(self.skip_stack)

        if raw_line.startswith("if "):
            if is_skipping:
                self.skip_stack.append(True)
            else:
                cond = raw_line[3:].replace("{", "").strip()
                res = self.eval_expr(cond, line_num, raw_line)
                self.skip_stack.append(not res if res is not None else True)
            return

        if raw_line.startswith("else"):
            if len(self.skip_stack) > 0:
                if len(self.skip_stack) == 1 or not any(self.skip_stack[:-1]):
                    self.skip_stack[-1] = not self.skip_stack[-1]
            return

        if is_skipping: return

        if push_m := re.match(r'push\s+to\s+(\w+)\((.*)\)', raw_line):
            name, val_expr = push_m.groups()
            if name in self.variables and isinstance(self.variables[name], list):
                val = self.eval_expr(val_expr, line_num, raw_line)
                self.variables[name].append(val)
                deb.log_var_change(f"{name}[]", val)
            else:
                deb.report_error("Array Error", f"'{name}' is not a list", line_num, raw_line)
            return

        if lib_m := re.match(r'incl\s+<(.*)>', raw_line):
            lib = lib_m.group(1)
            path = os.path.join("libr", f"{lib}.a")
            if os.path.exists(path): self.run_file(path)
            else: deb.report_error("Library Error", f"Package <{lib}> not found", line_num, raw_line)
            return

        if p_match := re.match(r'print@(\w+)\((.*)\)', raw_line):
            mod, content = p_match.groups()
            val = self.eval_expr(content, line_num, raw_line)
            if val is not None:
                print(val, end=" " if mod == "c" else "\n", flush=True)
            return

        if v_match := re.match(r'var\s+(\w+)\s*=\s*(.*);?', raw_line):
            name, val = v_match.groups()
            raw_val = val.replace(';', '').strip()
            if raw_val.startswith('[') and raw_val.endswith(']'):
                items = raw_val[1:-1].split(',')
                final_val = [self.eval_expr(i.strip(), line_num, raw_line) for i in items if i.strip()]
            else:
                final_val = self.eval_expr(raw_val, line_num, raw_line)
            self.variables[name] = final_val
            deb.log_var_change(name, final_val)
            return

        if for_m := re.match(r'for\s+(\w+)\s+(\d+),\s*(\d+)\s*\{', raw_line):
            self.recording_for = [for_m.group(1), int(for_m.group(2)), int(for_m.group(3)), []]

    def run_file(self, filepath):
        if not os.path.exists(filepath):
            deb.report_error("File Error", f"Source file '{filepath}' not found", 0)
            return
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1): self.execute_line(line, i)
