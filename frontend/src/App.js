import React, {Component} from 'react';
import {Navigate, Route, Routes} from "react-router";
import Home from "./components/home";
import Query from "./components/query";
import Status from "./components/status";

class App extends Component {
    render() {
        return (
            <main className="flex-shrink-0">
                <Routes>
                    <Route path="/" element={<Home/>}/>
                    <Route path="/status" element={<Status/>}/>
                    {/* A prefix query contains a slash, hence two segments */}
                    <Route path="/query/:query" element={<Query/>}/>
                    <Route path="/:category/:query" element={<Query/>}/>
                    <Route path="/:category/:query1/:query2" element={<Query/>}/>
                    <Route path="*" element={<Navigate to="/" replace/>}/>
                </Routes>
            </main>
        );
    }
}

export default App;
