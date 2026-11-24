import { useEffect, useState } from "react";
import { api } from "../../api/client";
import "./employees.css";
const roles = [
  ["operations_director", "Operations Director"],
  ["it_admin", "IT Administrator"],
  ["procurement_officer", "Procurement Officer"],
  ["store_worker", "Store / Warehouse"],
  ["sales_officer", "Sales Officer"],
  ["finance_officer", "Finance Officer"],
  ["auditor", "Auditor"],
];

const emptyForm = { name: "", username: "", email: "", role: "sales_officer", password: "" };

/** @typedef {{ id: number, name: string, username: string, email?: string | null, role: string, is_active: boolean }} Employee */

export default function Employees() {
  const [employees, setEmployees] = useState(/** @type {Employee[]} */([]));
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState(/** @type {Employee | null} */(null));
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [recovery, setRecovery] = useState(/** @type {{ username: string, code: string } | null} */(null));
  const [showTemporaryPassword, setShowTemporaryPassword] = useState(false);

  async function loadEmployees() {
    try {
      /** @type {{ employees?: Employee[] } | Employee[]} */
      const data = await api("/api/employees");
      setEmployees(Array.isArray(data) ? data : (data.employees || []));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load employees");
    }
  }

  useEffect(() => { loadEmployees(); }, []);

  /** @param {import("react").ChangeEvent<HTMLInputElement | HTMLSelectElement>} event */
  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function submitEmployee(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    try {
      if (editing) {
        await api(`/api/employees/${editing.id}`, {
          method: "PATCH",
          body: JSON.stringify({ name: form.name, username: form.username, email: form.email, role: form.role }),
        });
        setNotice("Employee updated.");
      } else {
        const data = await api("/api/employees", {
          method: "POST",
          body: JSON.stringify(form),
        });
        setNotice(data.temporary_password
          ? `Employee created. Temporary password: ${data.temporary_password}`
          : "Employee created.");
      }
      setForm(emptyForm);
      setEditing(null);
      await loadEmployees();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save employee");
    }
  }

  /** @param {Employee} employee */
  function editEmployee(employee) {
    setEditing(employee);
    setForm({ name: employee.name, username: employee.username, email: employee.email || "", role: employee.role, password: "" });
  }

  /** @param {Employee} employee
   *  @param {boolean} isActive
   */
  async function setAccess(employee, isActive) {
    setError("");
    try {
      await api(`/api/employees/${employee.id}/access`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: isActive }),
      });
      await loadEmployees();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update access");
    }
  }

  /** @param {Employee} employee */
  async function resetPassword(employee) {
    setError("");
    setNotice("");
    setRecovery(null);
    try {
      const data = await api(`/api/employees/${employee.id}/reset_password`, { method: "POST" });
      setRecovery({ username: employee.username, code: data.recovery_code });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to reset password");
    }
  }

  async function copyRecoveryCode() {
    if (!recovery) return;
    try {
      await navigator.clipboard.writeText(recovery.code);
      setNotice("Recovery code copied.");
    } catch {
      setError("Unable to copy the recovery code. Select it and copy manually.");
    }
  }

  /** @param {Employee} employee */
  async function removeEmployee(employee) {
    if (!window.confirm(`Delete ${employee.name}?`)) return;
    try {
      await api(`/api/employees/${employee.id}`, { method: "DELETE" });
      await loadEmployees();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete employee");
    }
  }

  return (
    <section>
      <div className="page-heading">
        <div><p className="eyebrow">Administration</p><h1>Employees</h1></div>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {notice && <div className="alert alert-success">{notice}</div>}
      {recovery && (
        <div className="recovery-code-card" role="status">
          <div>
            <strong>Recovery code for {recovery.username}</strong>
            <code>{recovery.code}</code>
            <small>Valid for 24 hours. The code is shown only once; copy it or issue it to the staff member now.</small>
          </div>
          <button type="button" className="secondary-button" onClick={copyRecoveryCode}>Copy code</button>
          <button type="button" className="secondary-button" onClick={() => setRecovery(null)}>Close</button>
        </div>
      )}

      <form className="employee-form" onSubmit={submitEmployee}>
        <h2>{editing ? "Edit employee" : "Add employee"}</h2>
        <div className="form-grid">
          <div><label>Name</label><input name="name" value={form.name} onChange={updateField} required /></div>
          <div><label>Username</label><input name="username" value={form.username} onChange={updateField} required /></div>
          <div><label>Email</label><input name="email" type="email" value={form.email} onChange={updateField} /></div>
          <div><label>Role</label><select name="role" value={form.role} onChange={updateField}>{roles.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div>
          {!editing && (
            <div>
              <label>Temporary password <span>(optional)</span></label>
              <div className="password-field">
                <input name="password" type={showTemporaryPassword ? "text" : "password"} value={form.password} onChange={updateField} />
                <button
                  className="password-toggle"
                  type="button"
                  aria-label={showTemporaryPassword ? "Hide temporary password" : "Show temporary password"}
                  aria-pressed={showTemporaryPassword}
                  onClick={() => setShowTemporaryPassword((visible) => !visible)}
                >
                  {showTemporaryPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>
          )}
        </div>
        <div className="button-row">
          <button className="primary-button" type="submit">{editing ? "Save changes" : "Create employee"}</button>
          {editing && <button className="secondary-button" type="button" onClick={() => { setEditing(null); setForm(emptyForm); }}>Cancel</button>}
        </div>
      </form>

      <div className="table-wrap">
        <table>
          <thead><tr><th>Name</th><th>Username</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>{employees.map((employee) => (
            <tr key={employee.id}>
              <td>{employee.name}<small>{employee.email || "—"}</small></td>
              <td>{employee.username}</td>
              <td>{roles.find(([value]) => value === employee.role)?.[1] || employee.role}</td>
              <td><span className={employee.is_active ? "status-active" : "status-inactive"}>{employee.is_active ? "Active" : "Disabled"}</span></td>
              <td className="actions">
                <button type="button" onClick={() => editEmployee(employee)}>Edit</button>
                <button type="button" onClick={() => resetPassword(employee)}>Reset</button>
                <button type="button" onClick={() => setAccess(employee, !employee.is_active)}>{employee.is_active ? "Disable" : "Restore"}</button>
                <button className="danger-link" type="button" onClick={() => removeEmployee(employee)}>Delete</button>
              </td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </section>
  );
}

