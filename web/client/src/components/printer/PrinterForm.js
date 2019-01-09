import _ from 'lodash';
import React, { Component } from 'react';
import { bindActionCreators } from "redux";
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Divider from '@material-ui/core/Divider';

import { updatePrinter } from '../../actions';

const styles = theme => ({
    container: {
        display: 'flex',
        flexWrap: 'wrap',
    },
    button: {
        margin: theme.spacing.unit,
    },
});

class PrinterFormComponent extends Component {
    state = {printer: null}

    componentDidMount() {
        const printerId = this.props.match.params.id;
        if (printerId.toUpperCase() === 'NEW') {
            this.setState({ printer: {} });
        } else {
            const printer = _.find(this.props.printers, {id: printerId});
            this.setState({printer});
        }
    }
    static getDerivedStateFromProps(nextProps, prevState) {
        if (prevState.printer == null && _.get(nextProps, 'printers')) {
            return {prin}
        }
        if (prevState.wasLoading && !nextProps.loading) {
            return ({ initLoaded: true, wasLoading: nextProps.loading });
        }
        return ({ wasLoading: nextProps.loading });
    }

    handleChange = name => event => {
        this.setState({
            [name]: event.target.value,
        });
    };

    render() {
        const { classes } = this.props;

        return (
            <Grid container spacing={24} justify='center'>
                <Grid item xs={12} md={8} lg={4}>
                    <form className={classes.container} noValidate autoComplete="off">
                        <TextField
                            id="standard-name"
                            label="Name"
                            className={classes.textField}
                            value={this.state.name}
                            onChange={this.handleChange('name')}
                            margin="normal"
                            fullWidth
                        />
                        <Divider />
                        <Button variant="contained">
                            Cancel
                        </Button>
                        <Button variant="contained" color="primary" >
                            Save
                        </Button>
                    </form>
                </Grid>
            </Grid>
        );
    }

    // actions

    updatePrinter = () => {
            const payload = { printer: this.state.printer };
            this.props.updatePrinter(payload);
    }
}

const mapDispatchToProps = dispatch => {
    return bindActionCreators(
        {
            updatePrinter,
        },
        dispatch
    );
};

export default connect(null, mapDispatchToProps)(withStyles(styles)(PrinterFormComponent));