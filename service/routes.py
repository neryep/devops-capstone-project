"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# LIST ALL ACCOUNTS
######################################################################


# ... place you code here to LIST accounts ...
@app.route("/accounts", methods=["GET"])
def list_accounts():
    """
    List all accounts
    This endpoint will return all accounts as a list of dictionaries
    """
    app.logger.info("Request to list all Accounts")
    accounts = Account.all()  # Fetch all accounts from the database
    results = [account.serialize() for account in accounts]  # Convert to JSON
    return jsonify(results), status.HTTP_200_OK
######################################################################
# READ AN ACCOUNT
######################################################################


# ... place you code here to READ an account ...
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    """
    Reads an Account
    This endpoint will return the account identified by account_id
    """
    app.logger.info("Request to read Account with id: %s", account_id)
    account = Account.find(account_id)
    if not account:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Account with id [{account_id}] could not be found.",
        )
    return jsonify(account.serialize()), status.HTTP_200_OK

######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################


# ... place you code here to UPDATE an account ...
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    """
    It should update an account by its ID
    """
    app.logger.info("Request to update Account with id: %s", account_id)

    account = Account.find(account_id)
    if not account:  # If account not found, return 404
        app.logger.error("Account with id %s not found.", account_id)
        abort(status.HTTP_404_NOT_FOUND, f"Account with id {account_id} not found")

    # Deserialize input data and update account
    app.logger.debug("Account found. Attempting to update.")
    account.deserialize(request.get_json())
    account.update()  # Save the changes in the database

    # Return the updated account with HTTP 200 status
    app.logger.info("Account with id %s updated successfully.", account_id)
    return jsonify(account.serialize()), status.HTTP_200_OK

######################################################################
# DELETE AN ACCOUNT
######################################################################


@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """
    It should delete an account by its ID
    """
    app.logger.info("Request to delete Account with id: %s", account_id)

    # Find the account by ID
    account = Account.find(account_id)
    if not account:
        return "", status.HTTP_204_NO_CONTENT  # Return 204 even if the account doesn't exist

    # Delete the account
    account.delete()

    # Return 204 No Content
    return "", status.HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
