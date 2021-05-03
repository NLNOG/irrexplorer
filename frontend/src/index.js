import React from 'react';
import ReactDOM from 'react-dom';

import App from './App';

import 'bootstrap/dist/css/bootstrap.css';
import './index.css';

import Footer from "./components/footer";

window.bootstrap = require('bootstrap/dist/js/bootstrap.bundle.js');


ReactDOM.render(
    <React.StrictMode>
        <App/>
    </React.StrictMode>,
    document.getElementById('root')
);


ReactDOM.render(
    <React.StrictMode>
        <Footer/>
    </React.StrictMode>,
    document.getElementById('footer')
);
