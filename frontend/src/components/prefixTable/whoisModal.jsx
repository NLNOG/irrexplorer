import React, {Component} from 'react';


class WhoisModal extends Component {
    constructor(props) {
        super(props);
        this.modal = {
            bootstrapModal: null,
            modalRef: React.createRef(),
            titleRef: React.createRef(),
            queryRef: React.createRef(),
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
        const {bootstrapModal, titleRef, queryRef, rpslTextRef, rpkiAlertRef} = this.modal;
        titleRef.current.innerText = `AS${asn} / ${prefix}`;
        queryRef.current.innerText = `whois -h whois.${sourceName}.net ${prefix}`;
        rpslTextRef.current.innerText = rpslText;
        rpkiAlertRef.current.hidden = rpkiStatus !== 'INVALID'
        bootstrapModal.show();
    }

    render() {
        const {modalRef, titleRef, queryRef, rpslTextRef, rpkiAlertRef} = this.modal;

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
                            <div className="alert alert-warning" role="alert" ref={rpkiAlertRef}>
                                This route object is RPKI invalid, and may be filtered out
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
