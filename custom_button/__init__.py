import os
from re import I
import streamlit.components.v1 as components
import streamlit as st

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _custom_button = components.declare_component(#반환값은 함수
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "custom_button", #이름
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))#root dir
    build_dir = os.path.join(parent_dir, "frontend/build")
    _custom_button = components.declare_component("custom_button", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def custom_button(label="", key=None, help=None, on_click=None, args=None, kwargs=None, *, type="secondary", disabled=False, use_container_width=False, width="auto", height="auto", font_size="10px"):
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    
    component_value = _custom_button(label=label, key=key, help=help, type=type, disabled=disabled, use_container_width=use_container_width, width=width, height=height, font_size=font_size)
    
    if component_value and on_click != None:
        if args != None:
            on_click(*args)
        elif kwargs != None:
            on_click(**kwargs)
        st.rerun()

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value


#(label, key=None, help=None, on_click=None, args=None, kwargs=None, *, type="secondary", disabled=False, use_container_width=False)