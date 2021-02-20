import React, {Component} from 'react';
import {Redirect, Router} from "@reach/router";
import Home from "./components/home";
import Search from "./components/search";

class App extends Component {
    render() {
        return (
            <main className="flex-shrink-0">
                <Router>
                    <Home path="/"/>
                    <Search path="/search/:search"/>
                    <Redirect default from="/" to="/" noThrow/>
                </Router>
            </main>
        );
    }
}

export default App;
