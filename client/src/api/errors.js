export function parseApiError(err) {
    if (!err.response) {
      return { status: null, message: "Cannot reach the server", fieldErrors: {} };
    }
  
    const { status, data } = err.response;
  
    // Marshmallow validation errors (400): { errors: { field: ["msg"] } }
    if (data?.errors) {
      const fieldErrors = Object.fromEntries(
        Object.entries(data.errors).map(([field, msgs]) => [field, [].concat(msgs).join(" ")])
      );
      return { status, message: "Please fix the highlighted fields", fieldErrors };
    }
  
    // Business-rule errors (404, 409, 422, 500): { error: "..." }
    let message = data?.error || "Something went wrong";
    if (data?.balance_due) message += ` (balance due: ${data.balance_due})`;
    if (data?.expected) message += ` (expected: ${data.expected})`;
  
    return { status, message, fieldErrors: {} };
  }