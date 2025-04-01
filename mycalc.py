import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Hello, PyGObject")
        self.set_default_size(300, 600)

        self.main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.main_vbox)

        self.buttons = Gtk.Grid()
        self.main_vbox.pack_start(self.buttons, True, True, 0)
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.scrollbar = Gtk.ScrolledWindow()
        self.scrollbar.add(self.textview)
        self.scrollbar.set_vexpand(True)
        self.current_line = 0        
        self.main_vbox.pack_start(self.scrollbar, True, True, 0)
        self.right_align_tag = self.textview.get_buffer().create_tag("right_align", justification=Gtk.Justification.RIGHT)
        self.previous_op = ''
        self.previous_button_char = ''
        self.num_digits = 0
        calc_labels = ['C', 'CE', '<X', '+/-', '7', '8', '9', '+', '4', '5', '6', '-', '1', '2', '3', '*', '=', '0', '.', '/']
        for i in range(5):
            for j in range(4):
                if (i*4+j) < len(calc_labels):
                    button = Gtk.Button(label=calc_labels[i*4+j])
                    button.connect("clicked", self.on_button_clicked)
                    self.buttons.attach(button, j, i, 1, 1)
        self.set_textview_lines_and_rows(1, 4)
        self.buffer = self.textview.get_buffer()
        start_iter = self.buffer.get_start_iter()
        end_iter = self.buffer.get_end_iter()
        self.buffer.apply_tag(self.right_align_tag, start_iter, end_iter)
        
    def set_textview_lines_and_rows(self, columns, rows):
        buffer = self.textview.get_buffer()
        text = '\n'.join(' ' * columns for _ in range(rows))
        buffer.set_text(text)

    def new_line(self):
        start_iter = self.buffer.get_start_iter()
        end_iter = self.buffer.get_end_iter()
        self.current_line += 1
        if self.current_line > 3:
            self.buffer.insert(end_iter, ' \n ')
        start_iter = self.buffer.get_start_iter()
        end_iter = self.buffer.get_end_iter()
        self.buffer.apply_tag(self.right_align_tag, start_iter, end_iter)                
  
    def scroll_buffer(self):
        end_iter = self.buffer.get_end_iter()
        mark = self.buffer.create_mark(None, end_iter, False)
        self.textview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

    def get_line(self, line_num):
        start_iter = self.buffer.get_iter_at_line_offset(line_num, 0)
        end_iter = start_iter.copy()
        end_iter.forward_to_line_end()
        return (start_iter, end_iter)

    def cursor_to_end(self):
        end_iter = self.buffer.get_end_iter()
        self.buffer.place_cursor(end_iter)

    def cursor_to_eol(self):
        cursor_iter = self.buffer.get_iter_at_mark(self.buffer.get_insert())
        cursor_iter.forward_to_line_end()
        self.buffer.place_cursor(cursor_iter)

    def place_cursor_at_line(self, line_num):
        iter = self.buffer.get_iter_at_line(line_num)
        self.buffer.place_cursor(iter)

    def get_text_for_line(self, line_num):
        (begin, end) = self.get_line(line_num)
        return self.buffer.get_text(begin, end, -1).strip(' ')
    
    def get_line_start_iter(self):
        cursor_iter = self.buffer.get_iter_at_mark(self.buffer.get_insert())
        return cursor_iter, self.buffer.get_iter_at_line(cursor_iter.get_line())
    
    def put_op_char(self, this_op):
        self.buffer.insert_at_cursor(this_op + '    ', -1)

    def validate_op(self, op):
        if self.previous_op == '=' and op in ['+', '-', '*', '/']:
            return True
        if self.num_digits == 0 and op in ['+', '-', '*', '/']:
            return False
        
        if op == '=':
            if self.previous_button_char in ['=','+', '-', '*', '/']:
                return False
            elif self.previous_op == '=':
                return False    
            elif self.previous_op in ['+', '-', '*', '/']:
                return True
            return False
        
        elif self.previous_button_char in ['+', '-', '*', '/']:
            return False
        return True

    def op_clicked_prepare(self, button):
        self.this_op = button.get_label()
        if not self.validate_op(self.this_op):
            return False
        if self.this_op in ['+', '-', '*', '/']:
            self.num_digits = 0
        if self.previous_op != '=':
            self.new_line()
            self.place_cursor_at_line(self.current_line)
        if self.previous_op != '=' and self.previous_op != '':
            self.put_op_char('=')
        elif self.previous_op == '':
            self.put_op_char(self.this_op)
        else:
            self.put_op_char(self.this_op)
        if self.current_line > 2:
            self.scroll_buffer()
        self.op = self.previous_op
        return True
    
    def op_clicked_do_math(self):    
        if self.current_line > 1 and self.op != '=':
            n1 = self.get_text_for_line(self.current_line - 2)
            n2 = self.get_text_for_line(self.current_line - 1)
            print(n1, self.op, n2)

            for char in ('+', '- ', '*', '/', '='):
                n1 = n1.replace(char, '')
                n2 = n2.replace(char, '')
                print(n1, self.op, n2)
            try:    
                result = eval(n1 + self.op + n2)
            except SyntaxError:
                return
            self.buffer.insert_at_cursor(str(result), -1)
            self.new_line()
            self.place_cursor_at_line(self.current_line)
            if self.this_op != '=':
                self.put_op_char(self.this_op)
        self.previous_op = self.this_op
        self.relocate_op_char(self.op)

    def do_special_key(self, button):
        op = button.get_label()
        print('key: ', op)
        if op == '+/-':
            if self.num_digits > 0:
                text = self.get_text_for_line(self.current_line)
                import re
                sign = re.sub('.*(.)[0-9]', r'\1', text)
                print('sign: ', sign)
                if sign == '-':
                    text = re.sub("([+|-|*|/] *)-([0-9]+)", r"\1\2", text)
                else:
                    text = re.sub("([+|-|*|/] *)([0-9]+)", r"\1-\2", text)
                self.buffer.delete(self.get_line(self.current_line)[0], 
                                   self.get_line(self.current_line)[-1])
                print('inserting: ', text)
                self.buffer.insert(self.buffer.get_iter_at_line(
                self.current_line), text)
                start_iter = self.buffer.get_start_iter()
                end_iter = self.buffer.get_end_iter()
                self.buffer.apply_tag(self.right_align_tag, start_iter, end_iter)                
                
                 
    def on_button_clicked(self, button, minus_sign='False'):
        
        if button.get_label() in ['=', '+', '-', '*', '/']:
            if self.op_clicked_prepare(button):
                self.op_clicked_do_math()

        elif button.get_label() in ['C', 'CE', '<X', "+/-"]:
            self.do_special_key(button)

        # place a digit
        else:
            if self.previous_op == '=':
                return
            print(button.get_label(), self.num_digits)
            if button.get_label() == '0' and self.num_digits == 0:
                return
            start_iter = self.buffer.get_iter_at_line(self.current_line)
            line_end = start_iter.copy()
            line_end.forward_to_line_end()
            self.buffer.place_cursor(line_end)
            self.buffer.insert_at_cursor(button.get_label(), -1)
            self.num_digits += 1
        self.previous_button_char = button.get_label()

    def place_cursor_at_line_offset(self, line, offset):
        iter = self.buffer.get_iter_at_line_offset(line, offset)
        self.buffer.place_cursor(iter)
    
    def get_cursor_position(self):
        cursor_mark = self.buffer.get_insert()
        cursor_iter = self.buffer.get_iter_at_mark(cursor_mark)
        line = cursor_iter.get_line()
        column = cursor_iter.get_line_offset()
        return line, column
        
    def relocate_op_char(self, op_char):
        print('the op is ', op_char)
        text = self.get_text_for_line(self.current_line - 2)
        print('text is:', text)
        if op_char not in text:
            return
        print('text: ', text)
        if len(op_char) == 0:
            return
        text = text.replace(op_char, '').strip(' ')
        padding_size = 20 - self.num_digits
        self.num_digits = 0
        text = op_char + text.rjust(padding_size, ' ') + ' '
        self.buffer.delete(self.get_line(self.current_line - 2)[0], 
                           self.get_line(self.current_line - 2)[-1])
        print('inserting: ', text)
        self.buffer.insert(self.buffer.get_iter_at_line(
            self.current_line - 2), text)

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()