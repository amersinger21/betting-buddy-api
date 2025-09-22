import { render } from "solid-js/web";
import { Router, Route } from "@solidjs/router";

import Home from "./pages/Home";
import Football from "./pages/Football";
import Baseball from "./pages/Baseball";
import Basketball from "./pages/Basketball";
import Error from "./pages/Error";
import App from "./App";
import "./index.css";

render(
  () => (
    <Router root={App}>
      <Route path="/" component={Home} />
      <Route path="/football" component={Football} />
      <Route path="/baseball" component={Error} />
      <Route path="/basketball" component={Error} />
    </Router>
  ),
  document.getElementById("root")
);
