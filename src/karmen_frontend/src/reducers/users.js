import dayjs from "dayjs";
import { persistUserProfile, dropUserProfile } from "../services/backend";

const getUserDataFromApiResponse = data => {
  return {
    currentState: data.force_pwd_change ? "pwd-change-required" : "logged-in",
    identity: data.identity,
    username: data.username,
    systemRole: data.system_role,
    hasFreshToken: data.fresh,
    accessTokenExpiresOn: data.expires_on ? dayjs(data.expires_on) : undefined,
    organizations: data.organizations,
    activeOrganization: data.organizations && data.organizations[0]
  };
};

export default (
  state = {
    me: {
      hasFreshToken: false,
      currentState: "logged-out",
      username: "",
      identity: null,
      systemRole: null,
      apiTokens: [],
      apiTokensLoaded: false,
      accessTokenExpiresOn: null,
      organizations: {},
      activeOrganization: null
    },
    list: [],
    listLoaded: false
  },
  action
) => {
  let userData;
  const { me } = state;
  switch (action.type) {
    case "USER_DATA_LOADED":
      userData = getUserDataFromApiResponse(action.payload.data);
      persistUserProfile(userData);
      return Object.assign({}, state, {
        me: {
          ...userData,
          apiTokens: [],
          apiTokensLoaded: false
        }
      });
    case "USER_AUTHENTICATE_FRESH_SUCCEEDED":
      if (action.payload.status !== 200) {
        return state;
      }
      userData = getUserDataFromApiResponse(action.payload.data);
      persistUserProfile(userData);
      return Object.assign({}, state, {
        me: {
          ...userData,
          apiTokens: [],
          apiTokensLoaded: false
        }
      });
    case "USER_AUTHENTICATE_SUCCEEDED":
      if (action.payload.status !== 200) {
        return state;
      }
      userData = getUserDataFromApiResponse(action.payload.data);
      persistUserProfile(userData);
      return Object.assign({}, state, {
        me: {
          ...userData,
          apiTokens: [],
          apiTokensLoaded: false
        }
      });
    case "USER_REFRESH_ACCESS_TOKEN_SUCCEEDED":
      if (action.payload.status !== 200) {
        return state;
      }
      userData = getUserDataFromApiResponse(action.payload.data);
      persistUserProfile(userData);
      return Object.assign({}, state, {
        me: Object.assign({}, state.me, userData)
      });
    case "USER_CHANGE_PASSWORD_SUCCEEDED":
      if (action.payload.status !== 200) {
        return state;
      }
      userData = getUserDataFromApiResponse(action.payload.data);
      persistUserProfile(userData);
      return Object.assign({}, state, {
        me: Object.assign({}, state.me, userData)
      });
    case "USER_CLEAR_ENDED":
      dropUserProfile();
      return Object.assign({}, state, {
        me: {
          currentState: "logged-out",
          hasFreshToken: false,
          accessTokenExpiresOn: null,
          identity: null,
          username: "",
          systemRole: null,
          apiTokens: [],
          apiTokensLoaded: false
        }
      });
    case "USER_LOAD_API_TOKENS_SUCCEEDED":
      return Object.assign({}, state, {
        me: Object.assign({}, state.me, {
          apiTokens: action.payload.data.items,
          apiTokensLoaded: true
        })
      });
    case "USER_ADD_API_TOKEN_SUCCEEDED":
      me.apiTokens.push({
        jti: action.payload.data.jti,
        name: action.payload.data.name,
        created: action.payload.data.created
      });
      return Object.assign({}, state, {
        me: Object.assign({}, state.me, {
          apiTokens: [].concat(me.apiTokens)
        })
      });
    case "USER_DELETE_API_TOKEN_SUCCEEDED":
      return Object.assign({}, state, {
        me: Object.assign({}, state.me, {
          apiTokens: me.apiTokens.filter(t => {
            return t.jti !== action.payload.jti;
          })
        })
      });
    case "USERS_LOAD_SUCCEEDED":
      if (action.payload.status !== 200) {
        return state;
      }
      if (!action.payload.data || !action.payload.data.items) {
        return state;
      }
      return Object.assign({}, state, {
        list: [].concat(action.payload.data.items),
        listLoaded: true
      });
    case "USERS_EDIT_SUCCEEDED":
      if (action.payload.data) {
        const userIndex = state.list.findIndex(
          u => u.uuid === action.payload.data.uuid
        );
        if (userIndex > -1) {
          state.list[userIndex].role = action.payload.data.role;
        }
      }
      return Object.assign({}, state, {
        list: [].concat(state.list)
      });
    case "USERS_DELETE_SUCCEEDED":
      if (action.payload.data) {
        const userIndex = state.list.findIndex(
          u => u.uuid === action.payload.data.uuid
        );
        if (userIndex > -1) {
          state.list = state.list
            .slice(0, userIndex)
            .concat(state.list.slice(userIndex + 1));
        }
      }
      return Object.assign({}, state, {
        list: [].concat(state.list)
      });
    case "USERS_CLEAR":
      return Object.assign({}, state, {
        list: []
      });
    default:
      return state;
  }
};
