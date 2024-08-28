function loadPlayerNames(sportID) {
	fetch(`http://129.80.84.210/api/sport_id=${sportID}`)
		.then((response) => response.json())
		.then((json) => console.log(json));
}
