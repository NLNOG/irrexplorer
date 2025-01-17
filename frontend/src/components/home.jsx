import React, {useEffect} from 'react';
import logo from "../logo.png";
import QueryForm from "./common/queryForm";

function Home() {
    useEffect(() => {
        document.title = 'IRR explorer';
    }, []);

    return (
        <div className="container-fluid d-flex justify-content-center">
            <div className="align-self-center">
                <div className="row">
                    <div className="col-sm-6 offset-sm-3">
                        <div className="text-center">
                            <img className="logo mb-5" src={logo} alt="IRR explorer"/>
                        </div>
                        <p className="lead">
                            IRR explorer shows the routing, IRR and RPKI status for resources,
                            and highlights potential issues.
                        </p>
                        <p>
                            Enter a prefix, IP address, AS number or AS/route set name.
                        </p>
                        <QueryForm/>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Home;
