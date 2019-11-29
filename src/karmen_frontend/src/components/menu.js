import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { clearUserIdentity, setCurrentState } from '../actions/users'

const Menu = ({ userState, username, role, logout, setCurrentUserState }) => {
  return (
    <nav>
      <h2 className="hidden">Navigation</h2>
      <Link to="/" className="karmen-logo" onClick={() => {
        if (userState === "fresh-token-required") {
          setCurrentUserState("logged-in");
        }
      }}>
        <img alt="Karmen logo" src="/logo.svg" />
      </Link>
      {userState === "logged-in" && (
        <ul className="navigation">
          <li>
            <Link to="/">Printers</Link>
          </li>
          <li>
            <Link to="/gcodes">G-Codes</Link>
          </li>
          {role === "admin" && (
            <li>
              <Link to="/users">Users</Link>
            </li>
          )}
          {role === "admin" && (
            <li>
              <Link to="/settings">Settings</Link>
            </li>
          )}
          <li>
            <Link to="/users/me">{username}</Link>
          </li>
          <li>
            <button className="plain" title="Logout" onClick={(e) => {
              e.preventDefault();
              logout();
            }}><i className="icon icon-exit"></i></button>
          </li>
        </ul>
      )}
    </nav>
  );
}

export default connect(
  state => ({
    userState: state.users.me.currentState,
    username: state.users.me.username,
    role: state.users.me.role,
  }),
  dispatch => ({
    logout: () => dispatch(clearUserIdentity()),
    setCurrentUserState: (userState) => dispatch(setCurrentState(userState)),
  })
)(Menu);