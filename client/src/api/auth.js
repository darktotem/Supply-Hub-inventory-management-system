import { api } from "./client";

export function login(username, password) {
  return api("/api/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function changePassword(oldPassword, newPassword) {
  return api("/api/change_password", {
    method: "PATCH",
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
  });
}

export function changeUsername(username, password) {
  return api("/api/change_username", {
    method: "PATCH",
    body: JSON.stringify({ username, password }),
  });
}

export function verifyRecoveryCode(username, recoveryCode) {
  return api("/api/verify_recovery_code", {
    method: "POST",
    body: JSON.stringify({ username, recovery_code: recoveryCode }),
  });
}

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

export function saveSession(token, user) {
  localStorage.setItem("supply_hub_token", token);
  localStorage.setItem("supply_hub_user", JSON.stringify(user));
}

export function getSavedToken() {
  return localStorage.getItem("supply_hub_token");
}

export function getSavedUser() {
  try {
    return JSON.parse(localStorage.getItem("supply_hub_user"));
  } catch {
    return null;
  }
}

export function clearSession() {
  localStorage.removeItem("supply_hub_token");
  localStorage.removeItem("supply_hub_user");
}
