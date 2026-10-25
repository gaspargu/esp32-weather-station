const dateFormatter = new Intl.DateTimeFormat("en", {
  dateStyle: "medium",
  timeStyle: "medium",
});

export const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

export function formatDate(value: string | null): string {
  return value === null ? "Not provided" : dateFormatter.format(new Date(value));
}
