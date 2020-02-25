import React from "react";
import { connect } from "react-redux";
import { Link, Redirect, withRouter } from "react-router-dom";
import { FormInputs } from "../components/forms/form-utils";
import BusyButton from "../components/utils/busy-button";
import Loader from "../components/utils/loader";
import { activate } from "../actions/users-me";

class RegisterConfirmation extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      tokenProcessed: false,
      email: undefined,
      activationKey: undefined,
      message: null,
      messageOk: false,
      passwordForm: {
        password: {
          name: "New password",
          val: "",
          type: "password",
          required: true
        },
        passwordConfirmation: {
          name: "New password confirmation",
          val: "",
          type: "password",
          required: true
        }
      }
    };
    this.activate = this.activate.bind(this);
  }

  componentDidMount() {
    const { location } = this.props;
    const params = new URLSearchParams(location.search);
    if (params.has("activate")) {
      try {
        console.log(params.get("activate"), atob(params.get("activate")));
        const tokenData = JSON.parse(atob(params.get("activate")));
        this.setState({
          email: tokenData.email,
          activationKey: tokenData.activation_key,
          tokenProcessed: true
        });
      } catch (e) {
        console.error(e);
        // silent pass as if no token was encountered
      }
    }
    this.setState({
      tokenProcessed: true
    });
  }

  activate(e) {
    e.preventDefault();
    const { passwordForm, email, activationKey } = this.state;
    const { doActivate } = this.props;
    let hasError = false;
    // eslint-disable-next-line no-unused-vars
    for (let field of Object.values(passwordForm)) {
      if (field.required && !field.val) {
        field.error = `${field.name} is required!`;
        hasError = true;
      } else {
        field.error = "";
      }
    }
    if (passwordForm.password.val) {
      if (passwordForm.password.val !== passwordForm.passwordConfirmation.val) {
        passwordForm.password.error = "Passwords do not match!";
        hasError = true;
      } else {
        passwordForm.password.error = "";
      }
    }

    if (hasError) {
      this.setState({
        passwordForm: Object.assign({}, passwordForm)
      });
      return;
    }

    return doActivate(
      email,
      activationKey,
      passwordForm.password.val,
      passwordForm.passwordConfirmation.val
    ).then(r => {
      if (r.status !== 200) {
        this.setState({
          messageOk: false,
          message:
            "Account activation failed. Maybe you could try to register again?"
        });
      } else {
        this.setState({
          message: "Account activated, please login with your new password",
          messageOk: true,
          passwordForm: Object.assign({}, passwordForm, {
            email: Object.assign({}, passwordForm.email, { val: "" })
          })
        });
      }
    });
  }

  render() {
    const {
      passwordForm,
      message,
      messageOk,
      tokenProcessed,
      email,
      activationKey
    } = this.state;
    const updateValue = (name, value) => {
      const { passwordForm } = this.state;
      this.setState({
        passwordForm: Object.assign({}, passwordForm, {
          [name]: Object.assign({}, passwordForm[name], {
            val: value,
            error: null
          })
        })
      });
    };

    if (!tokenProcessed) {
      return <Loader />;
    }

    if (tokenProcessed && (!email || !activationKey)) {
      // TODO or activation_key_expired
      // TODO this is not really user friendly
      return <Redirect to="/login" />;
    }

    return (
      <div className="content">
        <div className="container">
          <h1 className="main-title text-center">
            Welcome to Karmen, {email}!
          </h1>
          <form>
            <FormInputs definition={passwordForm} updateValue={updateValue} />

            <div className="form-messages">
              <p className="text-center">
                To start using Karmen You need to set the password.
              </p>

              {message && (
                <p
                  className={
                    messageOk
                      ? "text-success text-center"
                      : "message-error text-center"
                  }
                >
                  {message}
                </p>
              )}
            </div>

            <div className="cta-box text-center">
              <BusyButton
                className="btn"
                type="submit"
                onClick={this.activate}
                busyChildren="Sending link..."
              >
                Register
              </BusyButton>{" "}
              <Link to="/login" className="btn btn-plain">
                Cancel
              </Link>
            </div>
          </form>
        </div>
      </div>
    );
  }
}

export default withRouter(
  connect(undefined, dispatch => ({
    doActivate: (email, activationKey, password, passwordConfirmation) =>
      dispatch(activate(email, activationKey, password, passwordConfirmation))
  }))(RegisterConfirmation)
);
