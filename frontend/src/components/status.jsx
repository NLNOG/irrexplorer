import React, {useEffect} from 'react';
import logo from "../logo.png";
import Metadata from "./common/metadata";
import {Link} from "@reach/router";

function Status() {
    useEffect(() => {
        document.title = 'IRR explorer';
    }, []);

    return (<div className="container-fluid d-flex justify-content-center">
        <div className="align-self-center">
            <div className="row">
                <div className="col-sm-6 offset-sm-3 mt-5">
                    <Link to="/">
                        <img className="logo-small mb-5" src={logo} alt="IRR explorer"/>
                    </Link>
                    <h1>Data status</h1>
                    <p className="lead">
                        This page shows the last update times for all IRR explorer data sources.
                    </p>
                    <p>
                        <ul>
                            <li>Prefix to RIR mapping from RIRstats</li>
                            <li>Prefix to DFZ mapping from <a href="https://bgp.tools/">bgp.tools</a></li>
                            <li>
                                IRRs mirrored over NRTMv3 with
                                with <a href="https://irrd.readthedocs.io/en/stable/">IRRD v4</a>
                            </li>
                            <li>
                                RPKI data imported
                                through <a href="https://irrd.readthedocs.io/en/stable/">IRRD v4</a>
                            </li>
                        </ul>
                    </p>
                    <p>
                        Important notes:
                        <ul>
                            <li>
                                The RIRstats update time refers to the last time IRR explorer imported
                                the current files - not the original publication time of the files.
                            </li>
                            <li>
                                For IRR sources, the last update time is when IRRD last <em>processed</em> an update
                                for this source, not when it last <em>tried</em>.
                                For sources that rarely change, it is normal for the last update to be long ago.
                                This is due to limitations in NRTMv3.
                            </li>
                        </ul>
                    </p>
                    <Metadata/>

                </div>
            </div>
        </div>
    </div>);
}

export default Status;
