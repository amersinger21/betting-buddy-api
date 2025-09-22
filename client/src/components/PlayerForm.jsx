import { createResource } from "solid-js";

const fetchPlayers = async () => {
  const res = await fetch("http://129.80.84.210/api/players?sport_id=1");

  return res.json();
};

export default function Form(props) {
  const [players] = createResource(fetchPlayers);

  return (
    <>
      <form>
        <label for="playerName">Player Name</label>
        <input
          list="playerList"
          id="playerName"
          name="playerName"
          placeholder="Click to Search"
        />
        <datalist id="playerList">
          <For each={players()}>
            {(player) => (
              <option
                value={player.first_name + " " + player.last_name}
                data-id={player.id}
              ></option>
            )}
          </For>
        </datalist>
      </form>
      <p>{console.log(players())}</p>
    </>
  );
}
