import { A } from "@solidjs/router";
const App = (props) => (
  <>
    <nav>
      <A href="/">
        <h1>The Betting Buddy</h1>
      </A>
      <A href="/football">Football</A>
      <A href="/basketball">Basketball</A>
      <A href="/baseball">Baseball</A>
    </nav>
    {props.children}
  </>
);

export default App;
