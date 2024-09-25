const footbalStats = [
	{
		value: "pass_att",
		name: "Passing Attempts",
	},
	{
		value: "pass_comp",
		name: "Passing Completions",
	},
	{
		value: "pass_yards",
		name: "Passing Yards",
	},
	{
		value: "pass_td",
		name: "Passing TDs",
	},
	{
		value: "pass_longest",
		name: "Longest Pass",
	},
	{
		value: "ints",
		name: "Interceptions",
	},
	{
		value: "sacks",
		name: "Sacks",
	},
	{
		value: "rush_att",
		name: "Rush Attempts",
	},
	{
		value: "rush_yards",
		name: "Rush Yards",
	},
	{
		value: "rush_td",
		name: "Rush TDs",
	},
	{
		value: "rush_longest",
		name: "Longest Rush",
	},
	{
		value: "targets",
		name: "Targets",
	},
	{
		value: "rec",
		name: "Receptions",
	},
	{
		value: "rec_yards",
		name: "Receiving Yards",
	},
	{
		value: "rec_td",
		name: "Receiving TDs",
	},
	{
		value: "rec_longest",
		name: "Longest Reception",
	},
	{
		value: "fumbles",
		name: "Fumbles",
	},
];

const teamStats = [];

function loadFootballStats() {
	let playerStats = document.querySelector("#playerStat");

	for (let elements of footbalStats) {
		let option = document.createElement("sl-option");
		option.innerText = elements.name;
		option.value = elements.value;
		playerStats.appendChild(option);
	}
}
