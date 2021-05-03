import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Spinner from "../common/spinner";
import PrefixTableBody from "./prefixTableBody";
import {findIrrSourceColumns, sortPrefixesDataBy} from "../../utils/prefixData";
import PrefixTableHeader from "./prefixTableHeader";


class PrefixTable extends Component {
    state = {sortedPrefixesData: [], irrSourceColumns: []}

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
        this.updateState();
        this.modal.bootstrapModal = new window.bootstrap.Modal(this.modal.modalRef.current);
    }

    componentWillUnmount() {
        this.modal.bootstrapModal.dispose();
    }

    componentDidUpdate(prevProps) {
        if (prevProps.prefixesData !== this.props.prefixesData)
            this.updateState();
    }

    updateState() {
        this.setState({
            sortedPrefixesData: sortPrefixesDataBy(this.props.prefixesData, 'prefix'),
            irrSourceColumns: findIrrSourceColumns(this.props.prefixesData),
        });

    }

    handleSort = ({key, order}) => {
        const sortedPrefixesData = sortPrefixesDataBy(this.props.prefixesData, key, order);
        this.setState({sortedPrefixesData});
    }

    handleIrrRouteSelect = (prefix, asn, sourceName, rpslText, rpkiStatus) => {
        const {bootstrapModal, titleRef, queryRef, rpslTextRef, rpkiAlertRef} = this.modal;
        titleRef.current.innerText = `AS${asn} / ${prefix}`;
        queryRef.current.innerText = `whois -h whois.${sourceName}.net ${prefix}`;
        rpslTextRef.current.innerText = rpslText;
        rpkiAlertRef.current.hidden = rpkiStatus !== 'INVALID'
        bootstrapModal.show();
    }

    renderTableContent() {
        if (!this.props.hasLoaded)
            return this.renderTablePlaceholder(<Spinner/>);
        if (!this.props.prefixesData.length)
            return this.renderTablePlaceholder("No prefixes were found or query was too large to execute.");
        return <PrefixTableBody
            irrSourceColumns={this.state.irrSourceColumns}
            prefixesData={this.state.sortedPrefixesData}
            reducedColour={this.props.reducedColour}
            handleIrrRouteSelect={this.handleIrrRouteSelect}
        />
    }

    renderTablePlaceholder(placeholder) {
        return (
            <tbody>
            <tr>
                <td colSpan="5" className="text-center">{placeholder}</td>
            </tr>
            </tbody>
        );
    }

    render() {
        const {modalRef, titleRef, queryRef, rpslTextRef, rpkiAlertRef} = this.modal;
        return (
            <>
                <table className="table table-sm mb-5 table-fixed table-striped">
                    <PrefixTableHeader
                        irrSourceColumns={this.state.irrSourceColumns}
                        onSort={this.handleSort}
                        reducedColour={this.props.reducedColour}
                    />
                    {this.renderTableContent()}
                </table>
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
            </>
        );
    }
}

PrefixTable.propTypes = {
    prefixesData: PropTypes.arrayOf(PropTypes.object).isRequired,
    hasLoaded: PropTypes.bool,
    reducedColour: PropTypes.bool,
};


export default PrefixTable;
