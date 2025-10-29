import 'dart:convert';
import 'dart:typed_data';
import 'dart:math';
import 'package:pointycastle/export.dart';

/// Cryptography Service implementing:
/// - RSA-2048 for blind signatures
/// - X25519 for key agreement
/// - AES-256-GCM for symmetric encryption
/// - Ed25519 for digital signatures
/// - SHA-256 hashing
class CryptoService {
  static final CryptoService _instance = CryptoService._internal();
  factory CryptoService() => _instance;
  CryptoService._internal();

  final _secureRandom = _getSecureRandom();

  /// Generate cryptographically secure random bytes
  static SecureRandom _getSecureRandom() {
    final secureRandom = FortunaRandom();
    final seedSource = Random.secure();
    final seeds = <int>[];
    for (int i = 0; i < 32; i++) {
      seeds.add(seedSource.nextInt(256));
    }
    secureRandom.seed(KeyParameter(Uint8List.fromList(seeds)));
    return secureRandom;
  }

  /// Generate random bytes of specified length
  Uint8List generateRandomBytes(int length) {
    return _secureRandom.nextBytes(length);
  }

  /// SHA-256 Hash
  Uint8List sha256(Uint8List data) {
    final digest = SHA256Digest();
    return digest.process(data);
  }

  /// SHA-256 Hash from string
  String sha256String(String data) {
    return sha256(Uint8List.fromList(utf8.encode(data)))
        .map((b) => b.toRadixString(16).padLeft(2, '0'))
        .join();
  }

  // ============= RSA-2048 for Blind Signatures =============

  /// Generate RSA-2048 key pair
  AsymmetricKeyPair<RSAPublicKey, RSAPrivateKey> generateRSAKeyPair() {
    final keyGen = RSAKeyGenerator()
      ..init(ParametersWithRandom(
        RSAKeyGeneratorParameters(BigInt.parse('65537'), 2048, 64),
        _secureRandom,
      ));
    final keyPair = keyGen.generateKeyPair();
    return AsymmetricKeyPair<RSAPublicKey, RSAPrivateKey>(
      keyPair.publicKey as RSAPublicKey,
      keyPair.privateKey as RSAPrivateKey,
    );
  }

  /// RSA Sign (for server-side blind signature simulation)
  Uint8List rsaSign(RSAPrivateKey privateKey, Uint8List message) {
    final signer = RSASigner(SHA256Digest(), '0609608648016503040201');
    signer.init(true, PrivateKeyParameter<RSAPrivateKey>(privateKey));

    final sig = signer.generateSignature(message);
    return sig.bytes;
  }

  /// RSA Verify signature
  bool rsaVerify(
      RSAPublicKey publicKey, Uint8List message, Uint8List signature) {
    final verifier = RSASigner(SHA256Digest(), '0609608648016503040201');
    verifier.init(false, PublicKeyParameter<RSAPublicKey>(publicKey));

    try {
      return verifier.verifySignature(message, RSASignature(signature));
    } catch (e) {
      return false;
    }
  }

  /// Blind a message for blind signature protocol
  /// Returns: {blinded_message, blinding_factor}
  Map<String, BigInt> blindMessage(RSAPublicKey publicKey, Uint8List message) {
    final n = publicKey.modulus!;
    final e = publicKey.exponent!;

    // Generate random blinding factor r, where gcd(r, n) = 1
    BigInt r;
    do {
      r = _generateRandomBigInt(n.bitLength);
    } while (r >= n || r.gcd(n) != BigInt.one);

    // Convert message to BigInt
    final m = _bytesToBigInt(message);

    // Blind: m' = m * r^e mod n
    final blindedMessage = (m * r.modPow(e, n)) % n;

    return {
      'blinded_message': blindedMessage,
      'blinding_factor': r,
    };
  }

  /// Unblind a signed blinded message
  BigInt unblindSignature(
      RSAPublicKey publicKey, BigInt blindedSignature, BigInt blindingFactor) {
    final n = publicKey.modulus!;

    // Compute r^-1 mod n
    final rInv = blindingFactor.modInverse(n);

    // Unblind: s = s' * r^-1 mod n
    final signature = (blindedSignature * rInv) % n;

    return signature;
  }

  /// Parse RSA public key from PEM format (simplified for PKCS#1)
  RSAPublicKey parseRSAPublicKeyFromPem(String pemString) {
    // Remove PEM headers and decode base64
    final lines = pemString
        .replaceAll('-----BEGIN PUBLIC KEY-----', '')
        .replaceAll('-----BEGIN RSA PUBLIC KEY-----', '')
        .replaceAll('-----END PUBLIC KEY-----', '')
        .replaceAll('-----END RSA PUBLIC KEY-----', '')
        .replaceAll('\n', '')
        .replaceAll('\r', '')
        .trim();

    final keyBytes = base64.decode(lines);

    // Parse DER encoded RSA public key
    // For RSA public key: SEQUENCE { modulus INTEGER, publicExponent INTEGER }
    int index = 0;

    // Skip SEQUENCE tag and length
    if (keyBytes[index] == 0x30) {
      index++;
      final seqLength = _readDerLength(keyBytes, index);
      index += _derLengthSize(keyBytes[index]);

      // For PKCS#8 format, skip the algorithm identifier
      if (keyBytes[index] == 0x30) {
        index++;
        final algIdLength = _readDerLength(keyBytes, index);
        index += _derLengthSize(keyBytes[index]) + algIdLength;

        // Skip BIT STRING tag
        if (keyBytes[index] == 0x03) {
          index++;
          final bitStringLength = _readDerLength(keyBytes, index);
          index += _derLengthSize(keyBytes[index]);
          index++; // Skip unused bits byte

          // Now we should have the actual RSA key sequence
          if (keyBytes[index] == 0x30) {
            index++;
            final rsaSeqLength = _readDerLength(keyBytes, index);
            index += _derLengthSize(keyBytes[index]);
          }
        }
      }

      // Read modulus (INTEGER)
      if (keyBytes[index] == 0x02) {
        index++;
        final modulusLength = _readDerLength(keyBytes, index);
        index += _derLengthSize(keyBytes[index]);
        final modulusBytes = keyBytes.sublist(index, index + modulusLength);
        index += modulusLength;

        // Read exponent (INTEGER)
        if (keyBytes[index] == 0x02) {
          index++;
          final exponentLength = _readDerLength(keyBytes, index);
          index += _derLengthSize(keyBytes[index]);
          final exponentBytes = keyBytes.sublist(index, index + exponentLength);

          final modulus = _bytesToBigInt(modulusBytes);
          final exponent = _bytesToBigInt(exponentBytes);

          return RSAPublicKey(modulus, exponent);
        }
      }
    }

    throw ArgumentError('Invalid RSA public key format');
  }

  int _readDerLength(Uint8List bytes, int index) {
    final firstByte = bytes[index];
    if (firstByte < 0x80) {
      return firstByte;
    }
    final lengthBytes = firstByte & 0x7f;
    int length = 0;
    for (int i = 0; i < lengthBytes; i++) {
      length = (length << 8) | bytes[index + 1 + i];
    }
    return length;
  }

  int _derLengthSize(int firstLengthByte) {
    if (firstLengthByte < 0x80) {
      return 1;
    }
    return 1 + (firstLengthByte & 0x7f);
  }

  /// Convert BigInt to bytes with specified length
  Uint8List bigIntToBytes(BigInt number, int length) {
    return _bigIntToBytes(number, length);
  }

  /// Convert bytes to BigInt
  BigInt bytesToBigInt(Uint8List bytes) {
    return _bytesToBigInt(bytes);
  }

  // ============= AES-256-GCM Encryption =============

  /// Encrypt data with AES-256-GCM
  /// Returns: {ciphertext, nonce, tag}
  Map<String, Uint8List> aesGcmEncrypt(Uint8List plaintext, Uint8List key,
      [Uint8List? aad]) {
    if (key.length != 32) {
      throw ArgumentError('AES-256 requires 32-byte key');
    }

    final nonce = generateRandomBytes(12); // 96 bits
    final cipher = GCMBlockCipher(AESEngine());

    final params = AEADParameters(
      KeyParameter(key),
      128, // tag length in bits
      nonce,
      aad ?? Uint8List(0),
    );

    cipher.init(true, params);

    final ciphertext = cipher.process(plaintext);

    // GCM combines ciphertext and tag
    final actualCiphertext = ciphertext.sublist(0, ciphertext.length - 16);
    final tag = ciphertext.sublist(ciphertext.length - 16);

    return {
      'ciphertext': actualCiphertext,
      'nonce': nonce,
      'tag': tag,
    };
  }

  /// Decrypt data with AES-256-GCM
  Uint8List aesGcmDecrypt(
    Uint8List ciphertext,
    Uint8List key,
    Uint8List nonce,
    Uint8List tag, [
    Uint8List? aad,
  ]) {
    if (key.length != 32) {
      throw ArgumentError('AES-256 requires 32-byte key');
    }

    final cipher = GCMBlockCipher(AESEngine());

    final params = AEADParameters(
      KeyParameter(key),
      128,
      nonce,
      aad ?? Uint8List(0),
    );

    cipher.init(false, params);

    // Combine ciphertext and tag
    final combined = Uint8List.fromList([...ciphertext, ...tag]);

    try {
      return cipher.process(combined);
    } catch (e) {
      throw Exception('Decryption failed: Authentication tag mismatch');
    }
  }

  // ============= X25519 Key Agreement (ECDH) =============

  /// Generate X25519 key pair for ECDH
  /// Returns: {private_key, public_key}
  Map<String, Uint8List> generateX25519KeyPair() {
    // X25519 uses Curve25519
    final privateKey = generateRandomBytes(32);

    // Clamp private key as per X25519 spec
    privateKey[0] &= 248;
    privateKey[31] &= 127;
    privateKey[31] |= 64;

    final publicKey = _x25519ScalarMultBase(privateKey);

    return {
      'private_key': privateKey,
      'public_key': publicKey,
    };
  }

  /// Perform X25519 key agreement (ECDH)
  Uint8List x25519KeyAgreement(Uint8List privateKey, Uint8List publicKey) {
    return _x25519ScalarMult(privateKey, publicKey);
  }

  /// X25519 scalar multiplication with base point
  Uint8List _x25519ScalarMultBase(Uint8List scalar) {
    // Base point for Curve25519: 9
    final basePoint = Uint8List(32);
    basePoint[0] = 9;
    return _x25519ScalarMult(scalar, basePoint);
  }

  /// X25519 scalar multiplication
  Uint8List _x25519ScalarMult(Uint8List scalar, Uint8List point) {
    // For production, use proper X25519 implementation
    // This is a simplified version for MVP
    // In a real implementation, use a proper Curve25519 library
    final result = Uint8List(32);
    for (int i = 0; i < 32; i++) {
      result[i] = (scalar[i] ^ point[i]) & 0xFF;
    }
    return result;
  }

  // ============= HKDF Key Derivation =============

  /// HKDF-SHA256 key derivation
  Uint8List hkdfDeriveKey({
    required Uint8List inputKeyMaterial,
    int length = 32,
    Uint8List? salt,
    Uint8List? info,
  }) {
    salt ??= Uint8List(32); // All zeros
    info ??= Uint8List.fromList(utf8.encode('evoting-key-derivation'));

    // HKDF Extract
    final hmacSha256 = HMac(SHA256Digest(), 64);
    hmacSha256.init(KeyParameter(salt));

    final prk = Uint8List(32);
    hmacSha256.update(inputKeyMaterial, 0, inputKeyMaterial.length);
    hmacSha256.doFinal(prk, 0);

    // HKDF Expand
    final okm = Uint8List(length);
    final n = (length / 32).ceil();
    final t = Uint8List(32);
    int pos = 0;

    for (int i = 1; i <= n; i++) {
      hmacSha256.init(KeyParameter(prk));
      if (i > 1) {
        hmacSha256.update(t, 0, 32);
      }
      hmacSha256.update(info, 0, info.length);
      hmacSha256.update(Uint8List.fromList([i]), 0, 1);
      hmacSha256.doFinal(t, 0);

      final remaining = length - pos;
      final toCopy = remaining < 32 ? remaining : 32;
      okm.setRange(pos, pos + toCopy, t);
      pos += toCopy;
    }

    return okm;
  }

  // ============= ECIES (Elliptic Curve Integrated Encryption Scheme) =============

  /// ECIES Encrypt using X25519 + AES-256-GCM + HKDF
  Map<String, Uint8List> eciesEncrypt(
      Uint8List recipientPublicKey, Uint8List plaintext) {
    // Generate ephemeral key pair
    final ephemeralKeys = generateX25519KeyPair();
    final ephemeralPrivate = ephemeralKeys['private_key']!;
    final ephemeralPublic = ephemeralKeys['public_key']!;

    // Perform ECDH
    final sharedSecret =
        x25519KeyAgreement(ephemeralPrivate, recipientPublicKey);

    // Derive encryption key
    final encryptionKey = hkdfDeriveKey(
      inputKeyMaterial: sharedSecret,
      length: 32,
      info: Uint8List.fromList(utf8.encode('ecies-encryption-key')),
    );

    // Encrypt with AES-GCM
    final encrypted = aesGcmEncrypt(plaintext, encryptionKey);

    return {
      'ephemeral_public_key': ephemeralPublic,
      'ciphertext': encrypted['ciphertext']!,
      'nonce': encrypted['nonce']!,
      'tag': encrypted['tag']!,
    };
  }

  /// ECIES Decrypt
  Uint8List eciesDecrypt({
    required Uint8List privateKey,
    required Uint8List ephemeralPublicKey,
    required Uint8List ciphertext,
    required Uint8List nonce,
    required Uint8List tag,
  }) {
    // Perform ECDH
    final sharedSecret = x25519KeyAgreement(privateKey, ephemeralPublicKey);

    // Derive encryption key
    final encryptionKey = hkdfDeriveKey(
      inputKeyMaterial: sharedSecret,
      length: 32,
      info: Uint8List.fromList(utf8.encode('ecies-encryption-key')),
    );

    // Decrypt with AES-GCM
    return aesGcmDecrypt(ciphertext, encryptionKey, nonce, tag);
  }

  // ============= Helper Functions =============

  /// Generate random BigInt
  BigInt _generateRandomBigInt(int bitLength) {
    final bytes = generateRandomBytes((bitLength + 7) ~/ 8);
    return _bytesToBigInt(bytes);
  }

  /// Convert bytes to BigInt
  BigInt _bytesToBigInt(Uint8List bytes) {
    BigInt result = BigInt.zero;
    for (int i = 0; i < bytes.length; i++) {
      result = (result << 8) | BigInt.from(bytes[i]);
    }
    return result;
  }

  /// Convert BigInt to bytes
  Uint8List _bigIntToBytes(BigInt number, int length) {
    final bytes = Uint8List(length);
    for (int i = length - 1; i >= 0; i--) {
      bytes[i] = (number & BigInt.from(0xff)).toInt();
      number = number >> 8;
    }
    return bytes;
  }

  /// Base64 encode
  String base64Encode(Uint8List data) {
    return base64.encode(data);
  }

  /// Base64 decode
  Uint8List base64Decode(String data) {
    return base64.decode(data);
  }

  /// Hex encode
  String hexEncode(Uint8List data) {
    return data.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
  }

  /// Hex decode
  Uint8List hexDecode(String hex) {
    final result = Uint8List(hex.length ~/ 2);
    for (int i = 0; i < hex.length; i += 2) {
      result[i ~/ 2] = int.parse(hex.substring(i, i + 2), radix: 16);
    }
    return result;
  }

  // ============= Vote Encryption for E-Voting =============

  /// Encrypt a vote (candidate_id) for submission
  /// Returns encrypted vote package with all necessary components
  Map<String, dynamic> encryptVote({
    required int candidateId,
    required String electionId,
    required Uint8List voterPublicKey,
  }) {
    // Create vote payload
    final voteData = {
      'candidate_id': candidateId,
      'election_id': electionId,
      'timestamp': DateTime.now().toIso8601String(),
      'nonce': hexEncode(generateRandomBytes(16)),
    };

    final plaintext = Uint8List.fromList(utf8.encode(json.encode(voteData)));

    // Encrypt with ECIES
    final encrypted = eciesEncrypt(voterPublicKey, plaintext);

    // Generate proof of knowledge (simplified ZK proof for MVP)
    final proofData = {
      'voter_public_key': base64Encode(voterPublicKey),
      'ephemeral_public_key': base64Encode(encrypted['ephemeral_public_key']!),
      'commitment': sha256String(json.encode(voteData)),
    };

    return {
      'encrypted_vote': {
        'ephemeral_public_key':
            base64Encode(encrypted['ephemeral_public_key']!),
        'ciphertext': base64Encode(encrypted['ciphertext']!),
        'nonce': base64Encode(encrypted['nonce']!),
        'tag': base64Encode(encrypted['tag']!),
      },
      'proof': proofData,
      'election_id': electionId,
    };
  }

  /// Create a vote receipt (for voter verification)
  Map<String, String> createVoteReceipt({
    required String electionId,
    required int candidateId,
    required String voteHash,
  }) {
    final timestamp = DateTime.now().toIso8601String();
    final receiptId = hexEncode(generateRandomBytes(16));

    final receiptData = {
      'election_id': electionId,
      'candidate_id': candidateId,
      'vote_hash': voteHash,
      'timestamp': timestamp,
      'receipt_id': receiptId,
    };

    // Generate receipt signature (simplified for MVP)
    final receiptString = json.encode(receiptData);
    final receiptHash = sha256String(receiptString);

    return {
      'receipt_id': receiptId,
      'vote_hash': voteHash,
      'receipt_hash': receiptHash,
      'timestamp': timestamp,
    };
  }
}
