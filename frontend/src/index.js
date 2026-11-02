import React from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter} from 'react-router';

import App from './App';

import 'bootstrap/dist/css/bootstrap.css';
import './index.css';

import Footer from "./components/footer";

window.bootstrap = require('bootstrap/dist/js/bootstrap.bundle.js');


createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <BrowserRouter>
            <App/>
        </BrowserRouter>
    </React.StrictMode>
);


createRoot(document.getElementById('footer')).render(
    <React.StrictMode>
        <Footer/>
    </React.StrictMode>
);
