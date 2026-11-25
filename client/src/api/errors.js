export function parseApiError(err) {
  if (err?.response) {
    const { status, data } = err.response;

    if (data?.errors) {
      const fieldErrors = Object.fromEntries(
        Object.entries(data.errors).map(([field, msgs]) => [field, [].concat(msgs).join(" ")])
      );
      return { status, message: "Please fix the highlighted fields", fieldErrors };
    }

    let message = data?.error || "Something went wrong";
    if (data?.balance_due) message += ` (balance due: ${data.balance_due})`;
    if (data?.expected) message += ` (expected: ${data.expected})`;

    return { status, message, fieldErrors: {} };
  }

  const message = err instanceof Error ? err.message : String(err || "Something went wrong");
  return {
    status: null,
    message: message === "Cannot reach the server" ? message : message,
    fieldErrors: {},
  };
}