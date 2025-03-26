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

        calc_labels = ['7', '8', '9', '+', '4', '5', '6', '-', '1', '2', '3', '*', '=', '0', '.', '/']
        for i in range(4):
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
        return self.buffer.get_text(begin, end, -1).strip('=+1*/')
    
    def get_line_start_iter(self):
        cursor_iter = self.buffer.get_iter_at_mark(self.buffer.get_insert())
        return cursor_iter, self.buffer.get_iter_at_line(cursor_iter.get_line())
    
    def put_op_char(self, this_op):
        # Get the cursor position
        # cursor_iter, line_start_iter = self.get_line_start_iter()
        # Insert the character at the line start
        # self.buffer.insert(line_start_iter, this_op + '    ')
        # self.cursor_to_end()
    #    iter = self.buffer.get_iter_at_mark(self.buffer.get_insert())
    #    iter.forward_to_line_end()
    #    self.buffer.place_cursor(iter)
        self.buffer.insert_at_cursor(this_op + '    ', -1)
        # Move the cursor to the newly inserted character (optional)
        # cursor_iter, line_start_iter = self.get_line_start_iter()
        # new_cursor_iter = self.buffer.get_iter_at_line_offset(cursor_iter.get_line(), line_start_iter.get_offset() + 2) # +2 for the char and space
        # self.buffer.place_cursor(new_cursor_iter)

        # Ensure the cursor is visible
        # self.textview.scroll_to_iter(new_cursor_iter, 0.0, True, 0.0, 0.0)

    def on_button_clicked(self, button):
        if button.get_label() in ['=', '+', '-', '*', '/']:
            print('pb: ', self.previous_button_char)
            if self.previous_button_char in ['+', '-', '*', '/']:
                return
            self.this_op = button.get_label()
            
            if self.previous_op != '=':
                self.new_line()
            self.place_cursor_at_line(self.current_line)
            # self.cursor_to_eol()
            if self.previous_op != '=' and self.previous_op != '':
                self.put_op_char('=')
            elif self.previous_op == '':
                self.put_op_char(self.this_op)
            else:
                self.put_op_char(self.this_op)
            print('current line:', self.current_line)
            if self.current_line > 2:
                self.scroll_buffer()
            
            self.op = self.previous_op
            print('op:', self.op)
            print('previous op:', self.previous_op)
            
            if self.current_line > 1 and self.op != '=':
                n1 = self.get_text_for_line(self.current_line - 2)
                n2 = self.get_text_for_line(self.current_line - 1)
                print(n1, self.op, n2)
                for char in ('+', '-', '*', '/', '='):
                    n1 = n1.replace(char, '')
                    n2 = n2.replace(char, '')
                print(n1, self.op, n2)
                
                result = eval(n1 + self.op + n2)
                self.buffer.insert_at_cursor(str(result), -1)
                self.new_line()
                self.place_cursor_at_line(self.current_line)
                if self.this_op != '=':
                    self.put_op_char(self.this_op)
            self.previous_op = self.this_op
        else: # place a digit
            start_iter = self.buffer.get_iter_at_line(self.current_line)
            line_end = start_iter.copy()
            line_end.forward_to_line_end()
            self.buffer.place_cursor(line_end)
            
            self.buffer.insert_at_cursor(button.get_label(), -1)
            self.previous_button_char = button.get_label()

    def place_cursor_at_line_offset(self, line, offset):
        iter = self.buffer.get_iter_at_line_offset(line, offset)
        self.buffer.place_cursor(iter)
        # self.scroll_buffer(buffer)

    def get_cursor_position(self):
        cursor_mark = self.buffer.get_insert()
        cursor_iter = self.buffer.get_iter_at_mark(cursor_mark)
        line = cursor_iter.get_line()
        column = cursor_iter.get_line_offset()
        return line, column

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()