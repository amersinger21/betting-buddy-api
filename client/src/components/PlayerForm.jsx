import { createResource, createSignal } from "solid-js";
import submitPlayerForm from "../actions";

const fetchPlayers = async () => {
  const res = await fetch("http://129.80.84.210/api/players?sport_id=1");

  return res.json();
};

const [id, setID] = createSignal();
const [stat, setStat] = createSignal();
const [operator, setOperator] = createSignal();
const [amount, setAmount] = createSignal();

export default function Form(props) {
  const [players] = createResource(fetchPlayers);

  return (
    <>
      <form class="flexCol">
        <div class="flexCol">
          <label for="playerName">Player Name</label>
          <input
            list="playerList"
            id="playerName"
            name="playerName"
            placeholder="Click to Search"
            required
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
        </div>
        <div class="flexCol">
          <label for="stat">Stat</label>
          <input
            list="statList"
            id="stat"
            name="stat"
            placeholder="Choose a stat"
            required
          ></input>
          <datalist id="statList">
            <option value="Passing Attempts" data-stat="pass_att"></option>
            <option value="Passing Yards" data-stat="pass_yards"></option>
            <option value="Passing TDs" data-stat="pass_td"></option>
            <option value="Passing Completions" data-stat="pass_comp"></option>
            <option value="Longest Pass" data-stat="pass_longest"></option>
            <option value="Rushing TDs" data-stat="rush_att"></option>
            <option value="Rushing Attempts" data-stat="rush_att"></option>
            <option value="Rushing Yards" data-stat="rush_yards"></option>
            <option value="Rushing TDs" data-stat="rush_td"></option>
            <option value="Longest Rush" data-stat="rush_longest"></option>
            <option value="Receptions" data-stat="rec"></option>
            <option value="Targets" data-stat="targets"></option>
            <option value="Receiving Yards" data-stat="rec_yards"></option>
            <option value="Longest Reception" data-stat="rec_longest"></option>
            <option value="Receiving TDs" data-stat="rec_td"></option>
          </datalist>
        </div>
        <div class="flexCol">
          <label for="operator">Over/Under</label>
          <input
            list="operatorList"
            id="operator"
            name="operator"
            placeholder="Over/Under"
            required
          ></input>
          <datalist id="operatorList">
            <option value="Over" data-stat="over"></option>
            <option value="Under" data-stat="under"></option>
          </datalist>
        </div>
        <div class="flexCol">
          <label for="amount">Amount</label>
          <input
            type="number"
            min="0"
            step="5"
            id="amount"
            name="amount"
            placeholder="Choose an amount"
            required
          ></input>
        </div>
        <button type="submit" class="btn">
          Submit
        </button>
      </form>
    </>
  );
}
