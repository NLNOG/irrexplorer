import React, {Component} from 'react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faCheckCircle, faExclamationCircle, faSort, faSortDown} from '@fortawesome/free-solid-svg-icons'
import {faQuestionCircle, faTimesCircle} from "@fortawesome/free-regular-svg-icons";
import Spinner from "./common/spinner";
import SearchForm from "./common/searchForm";
import logo from "../logo.png";
import api from "../services/api";
import _ from 'lodash';

class Search extends Component {
    state = {prefixData: [], irrSourceColumns: []}
    searchInput() {
        return this.props.search
            ? this.props.search
            : this.props.search1 + '/' + this.props.search2;
    }

    async componentDidMount() {
        await this.loadPrefixData();
    }

    async loadPrefixData() {
        const prefixData = await api.getPrefixData(this.searchInput());
        let irrSources = [];
        prefixData.map(data => Object.keys(data.irrRoutes).map(irrRoute => irrSources.push(irrRoute)));
        const irrSourceColumns = _.uniq(irrSources);
        this.setState({prefixData, irrSourceColumns});
    }

    render() {
        return (
            <div className="container">
                <div className="row d-flex align-items-center mb-5">
                    <div className="col-lg-1">
                        <img className="logo-small" src={logo} alt="IRR explorer"/>
                    </div>
                    <div className="col-lg-5 offset-lg-1">
                        <SearchForm/>
                    </div>
                </div>
                <h1>Query: {this.searchInput()}</h1>
                {!this.state.prefixData.length && <Spinner/>}
                <table className="table table-hover table-sm">
                    <thead>
                    <tr>
                        <th scope="col">Prefix <FontAwesomeIcon icon={faSortDown}/></th>
                        <th scope="col">RIR <FontAwesomeIcon icon={faSort}/></th>
                        <th scope="col">BGP <FontAwesomeIcon icon={faSort}/></th>
                        {this.state.irrSourceColumns.map(sourceName =>
                            <th scope="col" key={sourceName}>{sourceName} <FontAwesomeIcon icon={faSort}/></th>
                        )}
                        <th scope="col">Advice</th>
                    </tr>
                    </thead>
                    <tbody>
                    {this.state.prefixData.map(prefixRow =>
                        <tr key={prefixRow.prefix}>
                            <td>{prefixRow.prefix}</td>
                            <td>{prefixRow.rir}</td>
                            <td>{prefixRow.bgpOrigins.join()}</td>
                            {this.state.irrSourceColumns.map(sourceName =>
                                prefixRow.irrRoutes[sourceName]
                                    ? <td key={sourceName}>{prefixRow.irrRoutes[sourceName].map(irrDetail => irrDetail.asn).join(", ")}</td>
                                    : <td />
                            )}
                            <td><span className="badge bg-success"><FontAwesomeIcon
                                icon={faCheckCircle}/> Everything good</span></td>
                        </tr>
                    )}
                    {/*<tr className="table-success">*/}
                    {/*    <td>2.57.252.0/24</td>*/}
                    {/*    <td>213279</td>*/}
                    {/*    <td>213279</td>*/}
                    {/*    <td>213279</td>*/}
                    {/*    <td><span className="badge bg-success"><FontAwesomeIcon*/}
                    {/*        icon={faCheckCircle}/> Everything good</span></td>*/}
                    {/*</tr>*/}
                    {/*<tr className="table-warning">*/}
                    {/*    <td>2.57.252.0/24</td>*/}
                    {/*    <td>213279</td>*/}
                    {/*    <td>65530</td>*/}
                    {/*    <td>213279</td>*/}
                    {/*    <td><span className="badge bg-warning"><FontAwesomeIcon icon={faExclamationCircle}/> Inconsistent origins</span>*/}
                    {/*    </td>*/}
                    {/*</tr>*/}
                    {/*<tr className="table-info">*/}
                    {/*    <td>2.57.252.0/24</td>*/}
                    {/*    <td>213279</td>*/}
                    {/*    <td>213279</td>*/}
                    {/*    <td>213279</td>*/}
                    {/*    <td><span className="badge bg-info"><FontAwesomeIcon icon={faQuestionCircle}/> Not seen in BGP, but (legacy?) route-objects exist, consider clean-up</span>*/}
                    {/*    </td>*/}
                    {/*</tr>*/}
                    {/*<tr className="table-danger">*/}
                    {/*    <td>2.57.252.0/24</td>*/}
                    {/*    <td>213279</td>*/}
                    {/*    <td/>*/}
                    {/*    <td/>*/}
                    {/*    <td><span className="badge bg-danger"><FontAwesomeIcon icon={faTimesCircle}/> Seen in DFZ, but no route object</span>*/}
                    {/*    </td>*/}
                    {/*</tr>*/}
                    </tbody>
                </table>
            </div>
        );
    }
}

export default Search;
