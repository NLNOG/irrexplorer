import React, {Component} from 'react';
import _ from 'lodash';

import Spinner from "./spinner";
import api from "../../services/api";
import TableFooter from "./tableFooter";
import dayjs from "dayjs";

const relativeTime = require('dayjs/plugin/relativeTime');

class Metadata extends Component {
    state = {
        hasLoaded: false, apiCallUrl: '', last_update_importer: null, last_update_irr: [],
    }

    async componentDidMount() {
        await this.loadData();
    }

    async loadData() {
        this.setState({
            hasLoaded: false, apiCallUrl: '', data: null,
        });
        const {data, url} = await api.getMetadata();
        this.setState({
            hasLoaded: true,
            apiCallUrl: url,
            last_update_importer: data.last_update.importer,
            last_update_irr: _.orderBy(Object.entries(data.last_update.irr)),
        });
    }

    renderTableContent() {
        const {hasLoaded, last_update_importer, last_update_irr, apiCallUrl} = this.state;
        if (!hasLoaded) return this.renderTablePlaceholder(<Spinner/>);
        console.debug(last_update_irr);
        return (<>
                <thead>
                <tr>
                    <th key="name" scope="col">Source</th>
                    <th key="name" scope="col">Last update</th>
                </tr>
                </thead>
                <tbody>
                <tr key="importer">
                    <td key="name">BGP and RIRstats</td>
                    <td key="last_update">{this.renderDate(last_update_importer)}</td>
                </tr>
                {last_update_irr.map(([source, last_update]) => <tr key={source}>
                    <td key="name">{source}</td>
                    <td key="last_update">{this.renderDate(last_update)}</td>
                </tr>)}
                </tbody>
                <TableFooter url={apiCallUrl}/>
            </>);
    }

    renderDate(date) {
        dayjs.extend(relativeTime);
        const date_parsed = dayjs(date);
        const format = 'YYYY-MM-DD HH:mm';
        return `${date_parsed.fromNow()} (${date_parsed.format(format)})`
    }

    renderTablePlaceholder(placeholder) {
        return (<tbody>
            <tr>
                <td className="text-center">{placeholder}</td>
            </tr>
            </tbody>);
    }

    render() {
        return (<table style={{width: 'auto'}} className="table table-fixed table-striped">
                {this.renderTableContent()}
            </table>);
    }
}

Metadata.propTypes = {};

export default Metadata;
