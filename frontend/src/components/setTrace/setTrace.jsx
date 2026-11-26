import React, {useEffect, useState} from 'react';
import PropTypes from 'prop-types';
import {Link, useSearchParams} from "react-router";

import api from "../../services/api";
import Spinner from "../common/spinner";
import AsnWithRPKIStatus from "../prefixTable/asnWithRPKIStatus";

// Merge the paths from the API into one tree below the traced set.
// Each path is [set, sub-set, ..., ASN]; the source belongs to the
// last set, the one listing the ASN.
export function buildTraceTree(target, paths) {
    const root = {name: target, children: new Map(), sources: []};
    for (const {path, source} of paths) {
        let node = root;
        for (const name of path.slice(1)) {
            if (!node.children.has(name))
                node.children.set(name, {name, children: new Map(), sources: []});
            node = node.children.get(name);
        }
        if (!node.sources.includes(source))
            node.sources.push(source);
    }
    return root;
}

function TraceNode({node}) {
    const isAsn = node.children.size === 0;
    return (
        <li>
            <Link to={`/query/${node.name}`} className={isAsn ? 'fw-bold' : ''}>{node.name}</Link>
            {isAsn && node.sources.length > 0 &&
                <small className="text-body-secondary ms-2">listed in {node.sources.join(', ')}</small>}
            {!isAsn &&
                <ul>
                    {[...node.children.values()].map(child => <TraceNode key={child.name} node={child}/>)}
                </ul>}
        </li>
    );
}

function TraceResult({data}) {
    const {target, query, origins, routes, paths, notIncluded, setFound} = data;
    const isPrefix = !/^AS\d+$/.test(query);

    if (isPrefix && !origins.length)
        return <p>No route(6) objects cover {query}, so there is no origin to trace.</p>;
    if (setFound === false)
        return <p>{target} was not found.</p>;

    return (
        <>
            {isPrefix &&
                <table className="table table-sm w-auto mb-3">
                    <caption className="caption-top">Route objects covering {query}</caption>
                    <thead>
                    <tr>
                        <th scope="col">Prefix</th>
                        <th scope="col">Origin</th>
                        <th scope="col">Source</th>
                    </tr>
                    </thead>
                    <tbody>
                    {routes.map(({prefix, asn, source, rpslPk, rpkiStatus, rpkiMaxLength}) =>
                        <tr key={rpslPk + source}>
                            <td className="font-monospace">
                                {prefix}{rpkiMaxLength && rpkiMaxLength !== Number(prefix.split('/')[1])
                                    ? ` (max length ${rpkiMaxLength})` : ''}
                            </td>
                            <td><AsnWithRPKIStatus asn={asn} rpkiStatus={rpkiStatus}/></td>
                            <td>{source}</td>
                        </tr>
                    )}
                    </tbody>
                </table>}

            {paths.length > 0 &&
                <ul className="set-trace-tree font-monospace">
                    <TraceNode node={buildTraceTree(target, paths)}/>
                </ul>}

            {notIncluded.length > 0 &&
                <div className="alert alert-warning w-auto d-inline-block" role="status">
                    Not included in {target}: {notIncluded.map(asn => `AS${asn}`).join(', ')}
                </div>}
        </>
    );
}

function SetTrace({setName}) {
    const [searchParams, setSearchParams] = useSearchParams();
    const trace = searchParams.get('trace') || '';
    const [input, setInput] = useState(trace);
    const [validationError, setValidationError] = useState('');
    const [result, setResult] = useState({hasLoaded: false, data: null, url: '', error: ''});

    useEffect(() => {
        setInput(trace);
        if (!trace) return;
        let current = true;
        setResult({hasLoaded: false, data: null, url: '', error: ''});
        api.getSetTrace(setName, trace).then(({data, url, error}) => {
            if (current)
                setResult({hasLoaded: true, data, url, error});
        });
        return () => {
            current = false;
        };
    }, [setName, trace]);

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!input) return;
        const cleanResult = await api.cleanQuery(input);
        if (cleanResult.error) {
            setValidationError(cleanResult.error);
        } else if (!['prefix', 'asn'].includes(cleanResult.category)) {
            setValidationError('Enter a prefix, IP address or ASN to trace.');
        } else {
            setSearchParams({trace: cleanResult.cleanedValue});
        }
    };

    const handleChange = ({currentTarget}) => {
        setValidationError('');
        setInput(currentTarget.value);
    };

    let content = null;
    if (trace) {
        if (!result.hasLoaded)
            content = <Spinner/>;
        else if (result.error)
            content = <p>{result.error}</p>;
        else if (result.data)
            content = <>
                <TraceResult data={result.data}/>
                <p className="text-end"><small><a href={result.url}>Source data as JSON</a></small></p>
            </>;
    }

    return (
        <>
            <h2 className="h3 mt-4">
                Trace:
            </h2>
            <hr/>
            <form className="row g-2 mb-3" onSubmit={handleSubmit}>
                <div className="col-sm-6 col-lg-4">
                    <label className="visually-hidden" htmlFor="trace">Prefix, IP or ASN to trace</label>
                    <input
                        type="text"
                        id="trace"
                        value={input}
                        placeholder="Prefix, IP or ASN"
                        onChange={handleChange}
                        className={'form-control' + (validationError ? ' is-invalid' : '')}
                        aria-describedby="trace-feedback"
                    />
                    <div className="invalid-feedback" id="trace-feedback">{validationError}</div>
                </div>
                <div className="col-auto">
                    <button type="submit" className="btn btn-success" disabled={!input}>Trace</button>
                </div>
            </form>
            <div aria-live="polite">{content}</div>
        </>
    );
}

SetTrace.propTypes = {
    setName: PropTypes.string.isRequired,
};

export default SetTrace;
