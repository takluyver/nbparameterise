"""Generate an HTML form based on notebook parameters.

Used by webapp.py
"""

import htmlgen

class Input(htmlgen.Element):
    type = htmlgen.html_attribute('type', default='text')
    name = htmlgen.html_attribute('name')
    value = htmlgen.html_attribute('value')

    def __init__(self, type, name=None, value=None):
        super().__init__("input")
        self.type = type
        if name is not None:
            self.name = name
        if value is not None:
            self.value = value

class Checkbox(Input):
    checked = htmlgen.boolean_html_attribute('checked')

    def __init__(self, name=None, checked=False):
        super().__init__(type="checkbox", name=name)
        self.checked=checked

class WrapperDiv(htmlgen.Division):
    def __init__(self, *children, css_classes=None, id=None):
        super().__init__()
        self.extend(children)
        if css_classes:
            self.add_css_classes(*css_classes)
        if id is not None:
            self.id = id

py_type_to_html_input_type = {
    str: 'text',
    int: 'number',
    float: 'number',
}

def make_input_element(var):
    if var.type is bool:
        input_elm = Checkbox(var.name, var.value)
    else:
        input_elm = Input(py_type_to_html_input_type[var.type], var.name,
                          str(var.value))
        if var.type is float:
            input_elm.set_attribute('step', 'any')
    
    return input_elm

def build_form(parameters, nbname):
    doc = htmlgen.Document(title="{} (input)".format(nbname))
    doc.add_stylesheets("https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css",
                        "https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css",
                        "/static/styles.css")
    doc.add_scripts("https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js",
                    "https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js")

    h1 = htmlgen.Heading(1, htmlgen.Emphasis(nbname))
    h1.append(' input')
    doc.append_body(h1)

    class MyForm(htmlgen.Element):
        action = htmlgen.html_attribute('action')
        
        def __init__(self):
            super().__init__("form")
            self.action = '/submit'
            self.set_attribute('method', 'post')
        
        def generate_children(self):
            for v in parameters:
                name = v.metadata.get('display_name', v.name)
                namediv = WrapperDiv(name, css_classes=['field-name'])
                input_elm = make_input_element(v)
                yield WrapperDiv(namediv, input_elm, css_classes=['form-field'])
            
            submit = Input('submit')
            submit.id  = 'submit-button'
            submit.set_attribute('value', 'Run notebook')
            submit.add_css_classes('btn', 'btn-success')
            yield WrapperDiv(submit, id='submit-div')
    
    container = htmlgen.Division()
    container.add_css_classes('container')
    container.append(MyForm())
    doc.append_body(container)
    return doc
