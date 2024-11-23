import React, {Component} from 'react';

import config from "../../config.json";


class WhoisModal extends Component {
    constructor(props) {
        super(props);
        this.modal = {
            bootstrapModal: null,
            modalRef: React.createRef(),
            titleRef: React.createRef(),
            queryRef: React.createRef(),
            queryUrlRef: React.createRef(),
            rpslTextRef: React.createRef(),
            rpkiAlertRef: React.createRef(),
        };
    }

    componentDidMount() {
        this.modal.bootstrapModal = new window.bootstrap.Modal(this.modal.modalRef.current);
    }

    componentWillUnmount() {
        this.modal.bootstrapModal.dispose();
    }

    openWithContent = (prefix, asn, sourceName, rpslText, rpkiStatus) => {
        const {bootstrapModal, titleRef, queryRef, queryUrlRef, rpslTextRef, rpkiAlertRef} = this.modal;
        const whoisServer = config.whoisServers[sourceName];
        const whoisUrl = config.whoisUrls[sourceName];
        titleRef.current.innerText = `AS${asn} / ${prefix}`;
        queryRef.current.innerText = `whois -h ${whoisServer} ${prefix}`;
        if (whoisUrl) {
            queryUrlRef.current.innerText = `Open this object on the ${sourceName} website`;
            queryUrlRef.current.href = whoisUrl.replace('SEARCHPLACEHOLDER', `${prefix}AS${asn}`);
            queryUrlRef.current.hidden = false;
        } else {
            queryUrlRef.current.hidden = true;
        }
        rpslTextRef.current.innerText = rpslText;
        rpkiAlertRef.current.hidden = rpkiStatus !== 'INVALID'
        bootstrapModal.show();
    }

    render() {
        const {modalRef, titleRef, queryRef, queryUrlRef, rpslTextRef, rpkiAlertRef} = this.modal;

        return (
            <div className="modal fade" tabIndex="-1" ref={modalRef}>
                <div className="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-lg">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h5 className="modal-title" ref={titleRef}>Modal title</h5>
                            <button type="button" className="btn-close" data-bs-dismiss="modal"
                                    aria-label="Close"/>
                        </div>
                        <div className="modal-body">
                            <p className="font-monospace" ref={queryRef}/>
                            <pre className="text-light bg-dark" ref={rpslTextRef}/>
                            <p>
                                The object shown below is mirrored, and may be modified or slightly outdated.
                                You can get the latest version directly from the IRR registry.
                            </p>
                            <p>
                                <a className="btn btn-success" href="/" ref={queryUrlRef}>#</a><br/>
                            </p>
                            <div className="alert alert-warning" role="alert" ref={rpkiAlertRef}>
                                This route object is RPKI-invalid, and may be filtered out
                                of whois query output by default.
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">Close
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}


WhoisModal.propTypes = {};

export default WhoisModal;
