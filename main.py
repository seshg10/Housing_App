# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import flask
from flask import Flask, render_template, request, Response, session, url_for, redirect
import numpy_financial as npf
import numpy as np
import random
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import os
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('APP_SECRET_KEY')

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField
from wtforms.validators import DataRequired


class Housing_Calculator_form(FlaskForm):
    '''
    Class defining data collected in the form data collected
    '''
    Housing_Cost = DecimalField('House Cost', validators=[DataRequired()])
    interest_rate = DecimalField('Interest Rate (%)', validators=[DataRequired()])
    term_loan = IntegerField('Term of Loan (years)', validators=[DataRequired()])


app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

"""
Main landing page route. Loading index_wtf.html which helps collect form data
"""
@app.route('/')
def index():
    form = Housing_Calculator_form()
    return render_template('index_wtf.html', form=form)

"""
Using data collected from the form to run computation
"""
@app.route('/', methods=['POST', 'GET'])
def house_cost():
    hcost = request.form.get('Housing_Cost', type=float)
    term_loan = request.form.get('term_loan', type=int)
    interest_rate = request.form.get('interest_rate', type=float) / (100 * 12)
    session["hcost"] = hcost
    session["term_loan"] = term_loan
    session["interest_rate"] = interest_rate
    monthly_payment = npf.pmt(interest_rate, term_loan * 12, hcost)
    value_s = ["${:,.2f}".format(hcost), interest_rate * 100 * 12, term_loan, round(-monthly_payment, 2)]
    return redirect(url_for('result'))

"""
Route loading result from the housing calculations
"""

@app.route('/result/', methods=['GET'])
def result():
    hcost = session.get("hcost")
    term_loan = session.get('term_loan')
    interest_rate = session.get("interest_rate")
    monthly_payment = npf.pmt(interest_rate, term_loan * 12, hcost)
    value_s = ["${:,.2f}".format(hcost), interest_rate * 100 * 12, term_loan, round(-monthly_payment, 2)]
    return render_template('result.html', value_s=value_s)


@app.route('/result/', methods=['POST'])
def result_post():
    print(request)
    return redirect(url_for('index'))

"""
Plot generation for the given input variables on the website
"""

@app.route('/plot/<type>.png')
def plot(type):
    hcost = session.get("hcost")
    term_loan = session.get('term_loan')
    interest_rate = session.get("interest_rate")
    [interest_payments, principal_payments] = payment_breakdown(hcost, term_loan, interest_rate)
    monthly_payment = npf.pmt(interest_rate, term_loan * 12, hcost)
    if (type == 'principal'):
        fig = mortgage_payments_fig(principal_payments / monthly_payment, term_loan, type=type)
    else:
        fig = mortgage_payments_fig(interest_payments / monthly_payment, term_loan, type=type)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def payment_breakdown(hcost, term_loan, interest_rate):
    """
    :param hcost: Cost of Home
    :param term_loan: Loan Term
    :param interest_rate: Interest Rate
    :return: interest payments and principal payments
    """
    interest_payments = np.zeros(term_loan * 12)
    principal_payments = np.zeros(term_loan * 12)
    for j in range(term_loan * 12):
        interest_payments[j] = npf.ipmt(interest_rate, j, term_loan * 12, hcost)
        principal_payments[j] = npf.ppmt(interest_rate, j, term_loan * 12, hcost)
    return (interest_payments, principal_payments)


def mortgage_payments_fig(payments, term_loan, type):
    """

    :param payments: Payment to be made per month
    :param term_loan: Length of loan
    :param type: Principal or Interest plot
    :return: Plot figure
    """
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    fig.patch.set_facecolor('#E8E5DA')

    x = range(term_loan * 12)
    y = payments

    axis.plot(x, y, color="#304C89")
    # print (x,y)
    if (type == 'principal'):
        axis.set_xlabel("Loan Period (months)", size=14)
        axis.set_ylabel("Fraction Payment as Principal", size=14)
    else:
        axis.set_xlabel("Loan Period (months)", size=14)
        axis.set_ylabel("Fraction Payment as Interest", size=14)

    return fig


def create_figure():
    """

    :return:Generates figure template
    """
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
