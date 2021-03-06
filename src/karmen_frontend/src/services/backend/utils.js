import dayjs from "dayjs";
import Cookies from "js-cookie";

import { HttpError, MaintenanceError } from "../../errors";

const BASE_URL = window.env.BACKEND_BASE;

const _removeStorage = (key) => {
  try {
    if (window.localStorage && window.localStorage.removeItem) {
      window.localStorage.removeItem(key);
    } else if (window.sessionStorage && window.sessionStorage.removeItem) {
      window.sessionStorage.removeItem(key);
    }
  } catch (e) {
    return null;
  }
};

const _setStorage = (key, value) => {
  try {
    if (value === null) {
      return _removeStorage(key);
    }
    if (window.localStorage && window.localStorage.setItem) {
      window.localStorage.setItem(key, value);
    } else if (window.sessionStorage && window.sessionStorage.setItem) {
      window.sessionStorage.setItem(value, value);
    }
  } catch (e) {
    return null;
  }
};

const _getStorage = (key) => {
  try {
    if (window.localStorage && window.localStorage.getItem) {
      return window.localStorage.getItem(key);
    } else if (window.sessionStorage && window.sessionStorage.getItem) {
      return window.sessionStorage.getItem(key);
    }
  } catch (e) {
    return null;
  }
  return null;
};

export const persistUserProfile = (data) => {
  _setStorage("karmen_profile", JSON.stringify(data));
};

export const dropUserProfile = () => {
  _setStorage("karmen_profile", null);
};

export const persistUserPreferences = (data) => {
  _setStorage("karmen_preferences", JSON.stringify(data));
};

export const dropUserPreferences = () => {
  _setStorage("karmen_preferences", null);
};

export const getUserPreferences = () => {
  return JSON.parse(_getStorage("karmen_preferences"));
};

export const getUserProfile = () => {
  const profile = JSON.parse(_getStorage("karmen_profile"));
  if (profile) {
    profile.accessTokenExpiresOn = dayjs(profile.accessTokenExpiresOn);
  }
  return profile;
};

export const getJsonPostHeaders = () => {
  const headers = new Headers();
  headers.set("Content-Type", "application/json");
  headers.set("X-CSRF-TOKEN", Cookies.get("csrf_access_token"));
  return headers;
};

export const performRequest = (opts) => {
  const defaults = {
    uri: undefined,
    data: undefined,
    method: "POST",
    successCodes: [200, 201, 202, 204],
    parseResponse: true,
    appendData: {},
    headers: {
      "Content-Type": "application/json",
    },
    useAuth: true,
  };
  opts = Object.assign({}, defaults, opts);



  let fetchOpts = {
    method: opts.method,
    headers: opts.headers,
  };
  // TODO this should probably merge with passed headers
  if (opts.useAuth) {
    fetchOpts.headers = getJsonPostHeaders();
    fetchOpts.headers.set("authorization", 'Bearer ' +Cookies.get("access_token_cookie"));
  }
  if (opts.data) {
    fetchOpts.body = JSON.stringify(opts.data);
  }
  if (!opts.uri.startsWith("/")) {
    opts.uri = `/${opts.uri}`;
  }
  return fetch(`${BASE_URL}${opts.uri}`, fetchOpts)
    .then((response) => {
      if (response.status === 503) {
        return Promise.reject(new MaintenanceError("Server under maitenance"));
      }

      if (opts.successCodes.indexOf(response.status) === -1) {
        return Promise.reject(
          new HttpError(response, `Unexpected status code "${response.status}"`)
        );
      }

      if (opts.parseResponse) {
        return response.json().then((data) => {
          return {
            status: response.status,
            ...opts.appendData,
            data,
            successCodes: opts.successCodes,
          };
        });
      }
      return {
        status: response.status,
        ...opts.appendData,
        successCodes: opts.successCodes,
      };
    })
    .catch((err) => {
      console.error(`Request ${opts.uri} failed: ${err}`);
      return Promise.reject(err);
    });
};
