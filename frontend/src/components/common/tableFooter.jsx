import React from 'react';

function TableFooter({url}) {
    if (!url) return null;
    return (
        <tfoot>
            <tr>
                <td colSpan="100%" className="text-end">
                    <small><a href={url}>Source data as JSON</a></small>
                </td>
            </tr>
        </tfoot>
    );
}

export default TableFooter;
