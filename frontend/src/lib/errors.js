// Turns your backend's enriched validation envelope into a simple
// { fieldName: "message" } map the forms can look up by field.
//
// Backend sends on a 422:
//   { error_type, message, details: [ { loc: ["body","amount"], msg: "..." }, ... ] }
// loc[0] is usually "body"; loc[1] is the field name. We key by loc[1].
//
// Returns { _general: "..." } for errors with no field (or non-422 errors)
// so the form can still show something.

export function fieldErrorsFrom(apiError) {
  const out = {};
  const details = apiError?.data?.details;

  if (Array.isArray(details) && details.length > 0) {
    for (const d of details) {
      const loc = d.loc || [];
      const field = loc.length > 1 ? loc[loc.length - 1] : "_general";
      if (!out[field]) out[field] = d.msg || "Invalid value";
    }
    return out;
  }

  // Not a field-level validation error (e.g. insufficient funds, 400/409).
  // Fall back to the envelope's top-level message.
  out._general = apiError?.data?.message || apiError?.message || "Something went wrong.";
  return out;
}
