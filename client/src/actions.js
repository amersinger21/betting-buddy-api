import { action, redirect } from "@solidjs/router";

const submitPlayerForm = action((formData) => {
  const id = formData.get("playerName");
  const stat = formData.get("stat");
  const operator = formData.get("operator");
  const amount = formData.get("amount");

  throw redirect(`/football?id=${id}`);
});

export default submitPlayerForm;
