async function loadPlayerNames(sportID) {
		const response = await fetch(`http://129.80.84.210/api/players?sport_id=${sportID}`);

		const json = await response.json();

		console.log(json);

		json.sort( function( a, b ) {
			a = a.last_name.toLowerCase();
			b = b.last_name.toLowerCase();
		
			return a < b ? -1 : a > b ? 1 : 0;
		});

		let playerName = document.querySelector("#playerName");

		for (let elements of json) {
			let option = document.createElement("sl-option");
			option.innerText = elements.first_name + " " + elements.last_name;
			option.value = elements.id;
			playerName.appendChild(option);
		}
		
	}
