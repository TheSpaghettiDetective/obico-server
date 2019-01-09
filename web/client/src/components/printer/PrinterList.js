import _ from 'lodash';
import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import { bindActionCreators } from "redux";
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import grey from '@material-ui/core/colors/grey';
import AddIcon from '@material-ui/icons/Add';

import Grid from '@material-ui/core/Grid';
import Fab from '@material-ui/core/Fab';

const styles = theme => ({
    margin: {
      margin: theme.spacing.unit,
    },
    addPrinterBox: {
        border: 'thin dashed',
        borderRadius: '0.5em',
        borderColor: grey[500],
        display: 'flex',
        flexFlow: 'column',
        minHeight: '12em',
        alignItems: 'center',
        justifyContent: 'center',
    }
  });

class PrinterListComponent extends Component {
    state = { printers: [] }

    render() {
        const { classes } = this.props;

        return (
            <Grid container spacing={24}>
                <Grid item xs={12} md={6} lg={4} className={classes.addPrinterBox}>
                    <Fab aria-label="Add" className={classes.margin} component={Link} to="/printers/new">
                        <AddIcon />
                    </Fab>
                    <div>Add Printer</div>
                </Grid>
            </Grid>
        )
    }
}

const mapStateToProps = state => {
    return {
        printers: _.get(state, 'printers', []),
        loading: _.get(state, 'loading.PRINTER_LIST_FETCH', false),
    }
};

export default connect(mapStateToProps, null)(withStyles(styles)(PrinterListComponent));