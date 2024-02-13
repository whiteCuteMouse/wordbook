import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import styled from '@emotion/styled'

interface State {
  //numClicks: number
    
    isClicked: boolean
    //isFocused: boolean
    //isOnClick: boolean
    //isHover: boolean
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */

class custom_button extends StreamlitComponentBase<State> {
    public state = { isClicked: false }//isFocused: false, isOnClick: false, isHover: falseisFocused: false,
    
  public render = (): ReactNode => {
    // Arguments that are passed to the plugin in Python are accessible
    // via `this.props.args`. Here, we access the "name" arg.
      const label = this.props.args["label"]
      //const on_click = this.props.args["on_click"]
      //const args = this.props.args["args"]
      const type = this.props.args["type"]
      const disabled = this.props.args["disabled"]
      const use_container_width = this.props.args["use_container_width"]
      const width = this.props.args["width"]
      const height = this.props.args["height"]
      const font_size = this.props.args["font_size"]

    // Streamlit sends us a theme object via props that we can use to ensure
    // that our component has visuals that match the active theme in a
    // streamlit app.
    const { theme } = this.props
    //const style: React.CSSProperties = {}
    
    // Maintain compatibility with older versions of Streamlit that don't send
      // a theme object.
    var Button = styled.button``
    if (theme) {
      // Use the theme object to style our button border. Alternatively, the
        // theme style is defined in CSS vars.

        if (type === "primary") {
            Button = styled.button`
            border:1px solid ${theme.primaryColor};
            color:white;
            background-color: ${theme.primaryColor};
            justify-content: center;
            font-weight: 400;
            padding: 0.25rem 0.75rem;
            border-radius: 0.5rem;
            min-height: 38.4px;
            margin: 0px;
            line-height: 1.6;
            width: auto;
            user-select: none;
            :hover{color:white; background-color:#FF3333; border:1px solid #FF3333}
            :active{color:hotpink; background-color:white}
            :focus{outline:none;}
            `
        }
        else if (type === "secondary") {
            Button = styled.button`
            border:1px solid #D6D6D9;
            color:black;
            background-color: white;
            justify-content: center;
            font-weight: 400;
            padding: 0.25rem 0.75rem;
            border-radius: 0.5rem;
            min-height: 38.4px;
            margin: 0px;
            line-height: 1.6;
            width: auto;
            user-select: none;
            :hover{color:${theme.primaryColor}; background-color:white; border:1px solid ${theme.primaryColor}}
            :focus{color:${theme.primaryColor}; background-color:white; border: 1px solid ${theme.primaryColor};outline:none;}
            :active{color:white; background-color:${theme.primaryColor}}
            `
        } else if (type === "custom") {
            Button = styled.button`
            border:1px solid #D6D6D9;
            color:black;
            background-color: white;
            justify-content: center;
            font-weight: 400;
            padding: 0.25rem 0.75rem;
            border-radius: 0.5rem;
            min-height: 38.4px;
            margin: 0px;
            line-height: 1.6;
            width: ${use_container_width ? "100%": width };
            height: ${height};
            user-select: none;
            font-size: ${font_size};
            :hover{color:${theme.primaryColor}; background-color:white; border:1px solid ${theme.primaryColor}}
            :focus{color:${theme.primaryColor}; background-color:white; border: 1px solid ${theme.primaryColor};outline:none;}
            :active{color:white; background-color:${theme.primaryColor}}
            `
        } else {
            Button = styled.button``
        }

        //style.display = "inline - flex"
        //style.fontWeight = 400
        //style.padding = "0.25rem 0.75rem"
        //style.borderRadius = "0.5rem"
        //style.minHeight = "38.4px"
        //style.margin = "0px"
        //style.lineHeight = 1.6
        //style.userSelect = "none"
        //style.justifyContent = "center"
    }
        //primaryColor during hover = "#FF4B4B"
     // primaryColor = "#F63366"
      //backgroundColor = "#FFFFFF"
      //secondaryBackgroundColor = "#F0F2F6"
      //textColor = "#262730"
      //font = "sans serif"

      // **** primary style button ****
      //display: inline - flex;
      //-moz - box - align: center;
      //align - items: center;
      //-moz - box - pack: center;
      //justify - content: center;
      //font - weight: 400;
      //padding: 0.25rem 0.75rem;
      //border - radius: 0.5rem;
      //min - height: 38.4px;
      //margin: 0px;
      //line - height: 1.6;
      //width: auto;
      //user - select: none;
      //background - color: rgb(255, 75, 75);
      //color: rgb(255, 255, 255);
      //border: 1px solid rgb(255, 75, 75);


    // Show a button and some text.
    // When the button is clicked, we'll increment our "numClicks" state
    // variable, and send its new value back to Streamlit, where it'll
      // be available to the Python program.

      const disabled_ = disabled ? true : this.props.disabled
    return (
        <span>
            <Button
                //class="custombutton"
                //style={style}
                onClick={this.onClicked}
                //disabled={this.props.disabled}
                //onFocus={this._onFocus}
                //onBlur={this._onBlur}
                //onMouseDownCapture={this._onMouseDownCapture}
                //onMouseUp={this._onMouseUpCapture}
                //onMouseOver={this._onMouseOver}
                //onMouseOut={this._onMouseOut}
                disabled={disabled_}
            >
                {label}
            </Button>
      </span>
    )
  }

  /** Click handler for the button. */
    private onClicked = (): void => {//클릭이 완료됐을 때
        //this.props.args["on_click"](this.props.args["args"])
      Streamlit.setComponentValue(true)
  }

  ///** Focus handler for our "Click Me!" button. */
  //private _onFocus = (): void => {
  //  this.setState({ isFocused: true })
  //}

  ///** Blur handler for our "Click Me!" button. */
  //private _onBlur = (): void => {
  //    this.setState({ isFocused: false })
  //    this.setState({ isClicked: false })
  //}
  //  private _onMouseDownCapture = (): void => {
  //      this.setState({ isOnClick: true })
  //  }
  //  private _onMouseUpCapture = (): void => {
  //      this.setState({ isOnClick: false })
  //  }

  //  private _onMouseOver = (): void => {
  //      this.setState({ isHover: true })
  //  }
  //  private _onMouseOut = (): void => {
  //      this.setState({ isHover: false })
  //  }
  //  private _onDragEnd = (): void => {
  //      this.setState({ isOnClick: false })
  //  }
}


//onClick: 사용자가 요소를 클릭했을 때 호출됩니다.
//onChange: input 요소의 값이 변경되었을 때 호출됩니다.
//onSubmit: form 요소가 제출되었을 때 호출됩니다.
//onFocus: 요소가 포커스를 받았을 때 호출됩니다.
//onBlur: 요소가 포커스를 잃었을 때 호출됩니다.
//onKeyPress: 키를 눌렀을 때 호출됩니다.
//onKeyUp: 키를 눌렀다 뗐을 때 호출됩니다.
//onKeyDown: 키를 눌렀을 때 호출됩니다.
//onMouseOver: 마우스가 요소 위에 올라갔을 때 호출됩니다.
//onMouseOut: 마우스가 요소에서 벗어났을 때 호출됩니다.
//onScroll: 요소가 스크롤될 때 호출됩니다.
//onDoubleClick: 요소를 더블 클릭했을 때 호출됩니다.
//onContextMenu: 요소를 우클릭했을 때 호출됩니다.
//onTouchStart: 터치가 시작될 때 호출됩니다.
//onTouchMove: 터치 동작 중일 때 호출됩니다.
//onTouchEnd: 터치가 종료될 때 호출됩니다.
//onTouchCancel: 터치가 취소될 때 호출됩니다.
//onDragStart: 드래그가 시작될 때 호출됩니다.
//onDrag: 드래그 중일 때 호출됩니다.
//onDragEnd: 드래그가 종료될 때 호출됩니다.
//onDrop: 요소 위에 놓인 아이템을 드롭했을 때 호출됩니다.

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(custom_button)
