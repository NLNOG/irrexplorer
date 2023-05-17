import React, {Component} from 'react';
import {Redirect, Router} from "@reach/router";
import Home from "./components/home";
import Query from "./components/query";
import Status from "./components/status";

class App extends Component {
    render() {
        return (
            <main className="flex-shrink-0">
                <Router>
                    <Home path="/"/>
                    <Status path="/status/"/>
                    {/* Reach does not have native support for a slash in the url, hence two Query paths */}
                    <Query path="/:category/:query"/>
                    <Query path="/:category/:query1/:query2"/>
                    <Redirect default from="/" to="/" noThrow/>
                </Router>
            </main>
        );
    }
}

export default App;
