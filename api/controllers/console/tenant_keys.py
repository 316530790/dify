from flask import jsonify, request
from flask_restx import Resource, fields
from sqlalchemy.orm import Session

from controllers.console import api
from core.helper import encrypter
from extensions.ext_database import db
from libs.rsa import generate_key_pair
from models.account import Tenant


class TenantKeyGenerateApi(Resource):
    def post(self, tenant_id):
        """Generate RSA key pair for tenant"""
        with Session(db.engine) as session:
            tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
            
            if not tenant:
                return {"error": "Tenant not found"}, 404
            
            if tenant.encrypt_public_key:
                return {"error": "Keys already exist for this tenant"}, 409
            
            public_key = generate_key_pair(tenant_id)
            
            tenant.encrypt_public_key = public_key
            session.commit()
            
            return {
                "result": "success", 
                "tenant_id": tenant_id,
                "public_key": public_key
            }, 201


class TenantKeyEncryptApi(Resource):
    """API密钥加密接口"""
    
    encrypt_request = api.model('EncryptRequest', {
        'api_key': fields.String(required=True, description='要加密的API密钥')
    })
    
    @api.expect(encrypt_request)
    def post(self, tenant_id):
        """
        根据租户ID加密API密钥
        使用与provider_credentials的encrypted_config相同的加密方式
        """
        try:
            data = request.get_json()
            if not data or 'api_key' not in data:
                return {"error": "Missing api_key in request body"}, 400
            
            api_key = data['api_key']
            if not api_key:
                return {"error": "api_key cannot be empty"}, 400
            
            # 验证租户是否存在
            with Session(db.engine) as session:
                tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
                if not tenant:
                    return {"error": "Tenant not found"}, 404
                
                if not tenant.encrypt_public_key:
                    return {"error": "Tenant encryption key not found. Please generate keys first."}, 404
            
            # 使用encrypter.encrypt_token进行加密，与provider_credentials保持一致
            encrypted_api_key = encrypter.encrypt_token(tenant_id, api_key)
            
            return {
                "result": "success",
                "tenant_id": tenant_id,
                "encrypted_api_key": encrypted_api_key,
                "original_length": len(api_key),
                "encrypted_length": len(encrypted_api_key)
            }, 200
            
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": f"Encryption failed: {str(e)}"}, 500


class TenantKeyDecryptApi(Resource):
    """API密钥解密接口"""
    
    decrypt_request = api.model('DecryptRequest', {
        'encrypted_api_key': fields.String(required=True, description='要解密的加密API密钥')
    })
    
    @api.expect(decrypt_request)
    def post(self, tenant_id):
        """
        根据租户ID解密API密钥
        使用与provider_credentials的encrypted_config相同的解密方式
        """
        try:
            data = request.get_json()
            if not data or 'encrypted_api_key' not in data:
                return {"error": "Missing encrypted_api_key in request body"}, 400
            
            encrypted_api_key = data['encrypted_api_key']
            if not encrypted_api_key:
                return {"error": "encrypted_api_key cannot be empty"}, 400
            
            # 验证租户是否存在
            with Session(db.engine) as session:
                tenant = session.query(Tenant).filter(Tenant.id == tenant_id).first()
                if not tenant:
                    return {"error": "Tenant not found"}, 404
            
            # 使用encrypter.decrypt_token进行解密，与provider_credentials保持一致
            decrypted_api_key = encrypter.decrypt_token(tenant_id, encrypted_api_key)
            
            # 为了安全起见，对解密后的密钥进行混淆显示
            obfuscated_key = encrypter.obfuscated_token(decrypted_api_key)
            
            return {
                "result": "success",
                "tenant_id": tenant_id,
                "decrypted_api_key": decrypted_api_key,
                "obfuscated_display": obfuscated_key,
                "decrypted_length": len(decrypted_api_key)
            }, 200
            
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": f"Decryption failed: {str(e)}"}, 500


def encrypt_api_key_for_tenant(tenant_id: str, api_key: str) -> str:
    """
    工具函数：为指定租户加密API密钥
    
    Args:
        tenant_id: 租户ID
        api_key: 要加密的API密钥
        
    Returns:
        str: 加密后的API密钥
        
    Raises:
        ValueError: 当租户不存在或加密失败时
    """
    try:
        return encrypter.encrypt_token(tenant_id, api_key)
    except Exception as e:
        raise ValueError(f"Failed to encrypt API key for tenant {tenant_id}: {str(e)}")


def decrypt_api_key_for_tenant(tenant_id: str, encrypted_api_key: str) -> str:
    """
    工具函数：为指定租户解密API密钥
    
    Args:
        tenant_id: 租户ID
        encrypted_api_key: 要解密的加密API密钥
        
    Returns:
        str: 解密后的API密钥
        
    Raises:
        ValueError: 当租户不存在或解密失败时
    """
    try:
        return encrypter.decrypt_token(tenant_id, encrypted_api_key)
    except Exception as e:
        raise ValueError(f"Failed to decrypt API key for tenant {tenant_id}: {str(e)}")


# Register API resources
api.add_resource(TenantKeyGenerateApi, "/tenants/<tenant_id>/keys/generate")
api.add_resource(TenantKeyEncryptApi, "/tenants/<tenant_id>/keys/encrypt")
api.add_resource(TenantKeyDecryptApi, "/tenants/<tenant_id>/keys/decrypt")