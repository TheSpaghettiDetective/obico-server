import React, { Component } from 'react';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Divider from '@material-ui/core/Divider';

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
    state = {}

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
}


export default withStyles(styles)(PrinterFormComponent);