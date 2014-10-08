import htmlgen

class Input(htmlgen.Element):
    type = htmlgen.html_attribute('type', default='text')
    name = htmlgen.html_attribute('name')
    def __init__(self, type, name=None):
        super().__init__("input")
        self.type = type
        if name is not None:
            self.name = name

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
    bool: 'checkbox',
}

def build_form(definitions, nbname):
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
            for v in definitions:
                namediv = WrapperDiv(v.name, css_classes=['field-name'])
                
                input_elm = Input(py_type_to_html_input_type[v.type], v.name)
                if v.type is float:
                    input_elm.set_attribute('step', 'any')

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