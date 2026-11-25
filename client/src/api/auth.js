import { api } from "./client";

/**
 * @typedef {{
 *   id: number,
 *   name: string,
 *   username: string,
 *   email?: string | null,
 *   role: string,
 *   is_active: boolean,
 *   must_change_password: boolean,
 *   created_at?: string | null
 * }} AuthUser
 */

/** @param {string} username @param {string} password @returns {Promise<{ token?: string, user?: AuthUser, mfa_required?: boolean, mfa_token?: string }>} */
export function login(username, password) {
  return api("/api/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

/** @param {string} mfaToken @param {string} code @returns {Promise<{ token: string, user: AuthUser }>} */
export function verifyMfa(mfaToken, code) {
  return api("/api/mfa/verify", {
    method: "POST",
    body: JSON.stringify({ mfa_token: mfaToken, code }),
  });
}

export function setupMfa() {
  return api("/api/mfa/setup", { method: "POST" });
}

/** @param {string} code */
export function enableMfa(code) {
  return api("/api/mfa/enable", { method: "POST", body: JSON.stringify({ code }) });
}

/** @param {string} oldPassword @param {string} newPassword @param {string} confirmPassword @returns {Promise<{ message: string }>} */
export function changePassword(oldPassword, newPassword, confirmPassword) {
  return api("/api/change_password", {
    method: "PATCH",
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword, confirm_password: confirmPassword }),
  });
}

/** @param {string} username @param {string} password @returns {Promise<{ user: AuthUser }>} */
export function changeUsername(username, password) {
  return api("/api/change_username", {
    method: "PATCH",
    body: JSON.stringify({ username, password }),
  });
}

/** @param {string} username @param {string} recoveryCode @returns {Promise<{ reset_token: string, expires_in_seconds: number }>} */
export function verifyRecoveryCode(username, recoveryCode) {
  return api("/api/verify_recovery_code", {
    method: "POST",
    body: JSON.stringify({ username, recovery_code: recoveryCode }),
  });
}

/** @param {string} resetToken @param {string} newPassword @param {string} confirmPassword @returns {Promise<{ message: string }>} */
export function setNewPassword(resetToken, newPassword, confirmPassword) {
  return api("/api/set_new_password", {
    method: "POST",
    body: JSON.stringify({
      reset_token: resetToken,
      new_password: newPassword,
      confirm_password: confirmPassword,
    }),
  });
}

/** @param {string} token @param {AuthUser} user @returns {void} */
export function saveSession(token, user) {
  localStorage.setItem("supply_hub_token", token);
  localStorage.setItem("supply_hub_user", JSON.stringify(user));
}

/** @returns {string | null} */
export function getSavedToken() {
  return localStorage.getItem("supply_hub_token");
}

/** @returns {AuthUser | null} */
export function getSavedUser() {
  try {
    const saved = localStorage.getItem("supply_hub_user");
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

export function clearSession() {
  localStorage.removeItem("supply_hub_token");
  localStorage.removeItem("supply_hub_user");
}
