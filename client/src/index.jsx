import { render } from "solid-js/web";
import { Router, Route, A } from "@solidjs/router";

import Home from "./pages/Home";
import Football from "./pages/Football";

const App = (props) => (
  <>
    <nav>
      <A href="/">Home</A>
      <A href="/football">Football</A>
    </nav>
    <h1>Site Title</h1>
    {props.children}
  </>
);

render(
  () => (
    <Router root={App}>
      <Route path="/" component={Home} />
      <Route path="/football" component={Football} />
    </Router>
  ),
  document.getElementById("root")
);
